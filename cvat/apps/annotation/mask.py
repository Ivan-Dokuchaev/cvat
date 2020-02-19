# Copyright (C) 2019 Intel Corporation
#
# SPDX-License-Identifier: MIT

format_spec = {
    "name": "MASK",
    "dumpers": [
        {
            "display_name": "{name} {format} {version}",
            "format": "ZIP",
            "version": "1.1",
            "handler": "dump",
        },
    ],
    "loaders": [
        {
            "display_name": "{name} {format} {version}",
            "format": "ZIP",
            "version": "1.1",
            "handler": "load",
        },
    ],
}


def dump(file_object, annotations):
    from cvat.apps.dataset_manager.bindings import CvatAnnotationsExtractor
    from cvat.apps.dataset_manager.util import make_zip_archive
    from datumaro.components.project import Environment
    from tempfile import TemporaryDirectory

    env = Environment()
    polygons_to_masks = env.transforms.get('polygons_to_masks')
    boxes_to_masks = env.transforms.get('boxes_to_masks')

    extractor = CvatAnnotationsExtractor('', annotations)
    extractor = extractor.transform(polygons_to_masks)
    extractor = extractor.transform(boxes_to_masks)
    converter = env.make_converter('voc_segmentation',
        apply_colormap=True, label_map='source')
    with TemporaryDirectory() as temp_dir:
        converter(extractor, save_dir=temp_dir)
        make_zip_archive(temp_dir, file_object)

def load(file_object, annotations):
    from pyunpack import Archive
    from tempfile import TemporaryDirectory
    from datumaro.plugins.voc_format.importer import VocImporter
    from datumaro.components.project import Environment
    from cvat.apps.dataset_manager.bindings import import_dm_annotations

    archive_file = file_object if isinstance(file_object, str) else getattr(file_object, "name")
    with TemporaryDirectory() as tmp_dir:
        Archive(archive_file).extractall(tmp_dir)

        dm_project = VocImporter()(tmp_dir)
        dm_dataset = dm_project.make_dataset()
        masks_to_polygons = Environment().transforms.get('masks_to_polygons')
        dm_dataset = dm_dataset.transform(masks_to_polygons)
        import_dm_annotations(dm_dataset, annotations)
