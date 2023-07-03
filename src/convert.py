import os
import shutil

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import get_file_name
from tqdm import tqdm

import src.settings as s


def download_dataset(teamfiles_ds_path: str) -> str:
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    file_info = api.file.get_info_by_path(team_id, teamfiles_ds_path)
    file_name_with_ext = file_info.name
    local_path = os.path.join(storage_dir, file_name_with_ext)
    dataset_path = os.path.splitext(local_path)[0]

    if not os.path.exists(dataset_path):
        sly.logger.info(f"Dataset dir '{dataset_path}' does not exist.")
        if not os.path.exists(local_path):
            sly.logger.info(f"Downloading archive '{teamfiles_ds_path}'...")
            api.file.download(team_id, teamfiles_ds_path, local_path)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        path = unpack_if_archive(local_path)
        sly.logger.info(f"Archive '{file_name_with_ext}' was unpacked successfully to: '{path}'.")
        sly.logger.info(f"Dataset dir contains: '{os.listdir(path)}'.")
        sly.fs.silent_remove(local_path)

    else:
        sly.logger.info(
            f"Archive '{file_name_with_ext}' was already unpacked to '{dataset_path}'. Skipping..."
        )
    return dataset_path


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    class_name = "pothole"
    label_ext = ".txt"
    class_id = 0
    # teamfiles_dir = "/Users/almaz/Downloads/archive-11"
    teamfiles_dir = "/4import/Pothole dataset v8 for detection/archive.zip"
    dataset_dir = download_dataset(teamfiles_dir)

    def _convert_geometry(x_center, y_center, ann_width, ann_height, img_width, img_height):
        x_center = float(x_center)
        y_center = float(y_center)
        ann_width = float(ann_width)
        ann_height = float(ann_height)

        px_x_center = x_center * img_width
        px_y_center = y_center * img_height

        px_ann_width = ann_width * img_width
        px_ann_height = ann_height * img_height

        left = px_x_center - (px_ann_width / 2)
        right = px_x_center + (px_ann_width / 2)

        top = px_y_center - (px_ann_height / 2)
        bottom = px_y_center + (px_ann_height / 2)

        return sly.Rectangle(top, left, bottom, right)

    def _parse_line(line, img_width, img_height, project_meta):
        line_parts = line.split()
        if len(line_parts) != 5:
            raise Exception("Invalid annotation format")
        else:
            cur_class_id, x_center, y_center, ann_width, ann_height = line_parts
            if int(cur_class_id) != class_id:
                raise Exception("Invalid class id")
            return sly.Label(
                _convert_geometry(x_center, y_center, ann_width, ann_height, img_width, img_height),
                project_meta.get_obj_class(class_name),
            )

    def _process_dir(input_dir, project, project_meta, api: sly.Api):
        split_paths = ["train", "valid", "train_to_valid"]
        images_dirname = "images"
        labels_dirname = "labels"
        for split_name in os.listdir(input_dir):
            if split_name == ".DS_Store":
                continue
            elif split_name == "only_rainy_frames":
                _process_dir(os.path.join(input_dir, split_name), project, project_meta, api)
            elif split_name in split_paths:
                dataset = api.dataset.get_info_by_name(project.id, split_name)
                if dataset is None:
                    dataset = api.dataset.create(project.id, split_name)
                split_path = os.path.join(input_dir, split_name)
                images_dir = os.path.join(split_path, images_dirname)
                labels_dir = os.path.join(split_path, labels_dirname)
                progress = tqdm(
                    desc=f"Processing {split_name} split", total=len(os.listdir(images_dir))
                )

                for batch in sly.batched(os.listdir(images_dir), batch_size=30):
                    if ".DS_Store" in batch:
                        batch.remove(".DS_Store")
                    image_paths = [os.path.join(images_dir, image_name) for image_name in batch]

                    image_infos = api.image.upload_paths(dataset.id, batch, image_paths)

                    def _create_ann(image_path):
                        img = sly.image.read(image_path)
                        height, width = img.shape[:2]
                        labels = []
                        file_name = os.path.basename(os.path.splitext(image_path)[0]) + label_ext
                        label_path = os.path.join(labels_dir, file_name)
                        if os.path.exists(label_path):
                            with open(label_path, "r") as f:
                                for line in f:
                                    try:
                                        label = _parse_line(line, width, height, project_meta)
                                        labels.append(label)
                                    except Exception as e:
                                        print(e)
                        ann = sly.Annotation(img_size=(height, width), labels=labels)
                        return ann

                    img_ids = [x.id for x in image_infos]

                    cur_anns = [_create_ann(image_path) for image_path in image_paths]
                    api.annotation.upload_anns(img_ids, cur_anns)
                    progress.update(len(batch))

    def _upload_project_meta(api, project_id):
        obj_class = sly.ObjClass(
            name=class_name, geometry_type=sly.Rectangle, color=sly.color.generate_rgb([])
        )
        project_meta = sly.ProjectMeta(obj_classes=sly.ObjClassCollection(items=[obj_class]))
        api.project.update_meta(project_id, project_meta.to_json())
        return project_meta

    project = api.project.create(workspace_id, project_name)
    
    project_meta = _upload_project_meta(api, project.id)

    _process_dir(dataset_dir, project, project_meta, api)

    # sly.logger.info('Deleting temporary app storage files...')
    # shutil.rmtree(storage_dir)

    return project
