# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals  # compatible with python3 unicode coding
from utils import dataset_util
import os
import numpy as np
import tensorflow as tf

from base.base_data_builder import BaseDataBuilder
from data.data_config import VisualGenomeDataConfig
from data.data_loader import VisualGenomeDataLoader
from data.data_utils import VisualGenomeDataUtils

data_config = VisualGenomeDataConfig()


class GQASceneGraphDataBuilder(BaseDataBuilder):
    """
    data builder for the scene graph of GQA
    """

    def __init__(self, data_config):
        super(GQASceneGraphDataBuilder, self).__init__(
            data_config=data_config
        )
        self.data_loader = VisualGenomeDataLoader()
        self.data_utils = VisualGenomeDataUtils()

    def __write_tf_examples(self, data_writer, tf_batch):
        for idx, example in enumerate(tf_batch):
            data_writer.write(example)
        print("saved {} tf_records".format(len(tf_batch)))
        pass

    def _build_data(self):
        scene_data_gen = self.data_loader.batch_load_scenegraph()
        data_file = os.path.join(self.data_config.train_data_dir, 'scene_graph_train.tfrecords')
        data_writer = tf.python_io.TFRecordWriter(data_file)
        tf_batch = list()
        batch_size = 100
        for batch, batch_datas in enumerate(scene_data_gen):
            for index, (image_id, image_data,image_object,image_width,image_height,questions) in enumerate(batch_datas):
                data = (image_id, image_data, image_object,image_width,image_height,questions)
                print("the file to example is {}".format(image_id))
                tf_example = self._to_tf_example(data)
                tf_batch.append(tf_example)
                if len(tf_batch) == batch_size:
                    self.__write_tf_examples(data_writer, tf_batch)
                    tf_batch = list()
        if len(tf_batch) > 0:
            self.__write_tf_examples(data_writer, tf_batch)
        del tf_batch
        pass


    def _to_tf_example(self, data):
        """
        convert data to tfrecord example
        :param data: region_graph json data
        :return:
        """
        image_id, image_data, image_object,image_width,image_height,questions = data
        image_data = np.asarray(image_data)
        #object

        object_id_list = list()
        object_name_list = list()
        object_x_list = list()
        object_y_list = list()
        object_h_list = list()
        object_w_list = list()
        object_attributes_list = list()
        object_relations_list = list()
        object_bbox_feature_list = list()

        for object in image_object:
            object_id = int(object)
            object_name = image_object[object]["name"]
            object_h = image_object[object]["h"]
            object_w = image_object[object]["w"]
            object_x = image_object[object]["x"]
            object_y = image_object[object]["y"]
            object_attributes = image_object[object]["attributes"]
            object_relations = image_object[object]["relations"]
            object_feature = image_object[object]["bbox_feature"]
            #填充数据
            object_id_list.append(object_id)
            object_name_list.append(object_name)
            object_x_list.append(int(object_x))
            object_y_list.append(int(object_y))
            object_h_list.append(int(object_h))
            object_w_list.append(int(object_w))
            object_attributes_list.append(object_attributes)
            object_relations_list.append(object_relations)
            object_bbox_feature_list.append(object_feature)
        print("------------------------------")
        print("object id len = {} ,object name len = {}".format(len(object_id_list),len(object_name_list)))

        object_name_nparray = np.asarray(object_name_list)
        object_attributes_nparray = np.asarray(object_attributes_list)
        object_relations_nparray = np.asarray(object_relations_list)
        object_feature_nparray = np.asarray(object_bbox_feature_list)

        #question data
        questionId_list = list()
        group_list = list()
        answer_list = list()
        type_list = list()
        question_list = list()
        fullAnswer_list = list()

        for question_item in questions:
            questionId = question_item["006121"]
            group =question_item["group"]
            answer = question_item["answer"]
            type = question_item["type"]
            question = question_item["question"]
            fullAnswer = question_item["fullAnswer"]
            # 填充数据
            questionId_list.append(questionId)
            group_list.append(group)
            answer_list.append(answer)
            type_list.append(type)
            question_list.append(question)
            fullAnswer_list.append(fullAnswer)
        print("------------------------------")
        print("question id len = {}".format(len(questionId_list)))

        questionId_nparray = np.asarray(questionId_list)
        group_nparray = np.asarray(group_list)
        answer_nparray = np.asarray(answer_list)
        type_nparray = np.asarray(type_list)
        question_nparray = np.asarray(question_list)
        fullAnswer_nparray = np.asarray(fullAnswer_list)



        features = tf.train.Features(feature={
            # image data
            'image/image_id': dataset_util.int64_feature(int(image_id)),
            'image/height': dataset_util.int64_feature(image_height),
            'image/width': dataset_util.int64_feature(image_width),
            'image/feature': dataset_util.bytes_feature(image_data.tobytes()),
            # object
            'image/object_id': dataset_util.int64_list_feature(object_id_list),

            'image/object_name':dataset_util.bytes_feature(object_name_nparray.tobytes()),

            'image/object_x':dataset_util.int64_list_feature(np.asarray(object_x_list)),
            'image/object_y': dataset_util.int64_list_feature(np.asarray(object_y_list)),
            'image/object_w': dataset_util.int64_list_feature(np.asarray(object_w_list)),
            'image/object_h': dataset_util.int64_list_feature(np.asarray(object_h_list)),

            'image/object_attributes': dataset_util.bytes_feature(object_attributes_nparray.tobytes()),
            'image/object_relations': dataset_util.bytes_feature(object_relations_nparray.tobytes()),
            'image/object_feature': dataset_util.bytes_feature(object_feature_nparray.tobytes()),
            #question
            'image/question/id': dataset_util.bytes_feature(questionId_nparray.tobytes()),
            'image/question/group': dataset_util.bytes_feature(group_nparray.tobytes()),
            'image/question/answer': dataset_util.bytes_feature(answer_nparray.tobytes()),
            'image/question/type': dataset_util.bytes_feature(type_nparray.tobytes()),
            'image/question/question':dataset_util.bytes_feature(question_nparray.tobytes()),
            'image/question/fullAnswer':dataset_util.bytes_feature(fullAnswer_nparray.tobytes())

        })
        tf_example = tf.train.Example(features=features)
        return  tf_example.SerializeToString()

if __name__ == '__main__':
    data_config = VisualGenomeDataConfig()
    region_data_prepare = GQASceneGraphDataBuilder(data_config)
    region_data_prepare._build_data()



