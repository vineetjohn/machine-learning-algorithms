import numpy as np
import math

from processors.processor import Processor
from utils import file_helper
from utils import log_helper

log = log_helper.get_logger("GaussianMixtureProcessor")

file_range = range(1, 6)


def get_class_covariance(class_vectors, mean, dimensions, train_set_size):

    final_matrix = np.zeros((dimensions, dimensions))

    for i in range(len(class_vectors)):
        vector = np.subtract(np.array(class_vectors[i]), mean)
        matrix = np.outer(vector, np.transpose(vector))
        final_matrix = np.add(final_matrix, matrix)

    return final_matrix/train_set_size


def normalize_probability_weights(current_probability_weights):
    sum_of_probabilities = 0
    for label in current_probability_weights.keys():
        sum_of_probabilities += current_probability_weights[label]

    if sum_of_probabilities != 1:
        factor = 1 / sum_of_probabilities
        for label in current_probability_weights.keys():
            current_probability_weights[label] *= factor

    return current_probability_weights


class GaussianMixtureProcessor(Processor):

    def process(self):
        log.info("GaussianMixtureProcessor begun")

        train_set_vectors, train_set_labels, test_set_vectors, test_set_labels, _, _, _, _ = \
            file_helper.get_datasets(self.options.input_data_folder, file_range)

        accuracy = self.run_classifier(train_set_vectors, train_set_labels, test_set_vectors, test_set_labels)
        log.info("Accuracy: " + str(accuracy))

        log.info("GaussianMixtureProcessor concluded")

    def run_classifier(self, train_set_vectors, train_set_labels, test_set_vectors, test_set_labels):

        distinct_labels = set(train_set_labels)
        train_set_size = len(train_set_vectors)
        dimensions = len(train_set_vectors[0])
        covariance_matrix = np.zeros((dimensions, dimensions))
        class_properties = dict()

        label_train_vectors = dict()
        for i in range(len(train_set_vectors)):
            key = train_set_labels[i]
            if key in label_train_vectors:
                vectors = label_train_vectors[key]
            else:
                vectors = list()
            vectors.append(train_set_vectors[i])
            label_train_vectors[key] = vectors

        for label in distinct_labels:
            class_count = len(label_train_vectors[label])
            prior = class_count/len(train_set_labels)
            mean = np.mean(np.array(label_train_vectors[label]), axis=0)

            property = dict()
            property['mean'] = mean
            property['prior'] = prior
            class_properties[label] = property

            class_covariance_matrix = \
                get_class_covariance(
                    label_train_vectors[label], mean, dimensions, train_set_size
                )
            covariance_matrix = np.add(covariance_matrix, class_covariance_matrix)

        log.info("class_properties: " + str(class_properties))
        log.info("covariance matrix:\n" + str(covariance_matrix))
        inv_covariance_matrix = np.linalg.inv(covariance_matrix)
        accuracy_count = 0

        for i in range(len(test_set_vectors)):
            denom_term = 0
            for label in distinct_labels:
                vector_deviation = (test_set_vectors[i] - class_properties[label]['mean'])
                expt_term = np.matmul(np.matmul(vector_deviation, inv_covariance_matrix), vector_deviation)
                denom_term += class_properties[label]['prior'] * math.exp(-0.5 * expt_term)

            correct_label = test_set_labels[i]
            log.debug("correct_label: " + str(correct_label))

            log.debug(test_set_vectors[i])
            class_probabilities = dict()
            for label in distinct_labels:
                vector_deviation = (test_set_vectors[i] - class_properties[label]['mean'])
                expt_term = np.matmul(np.matmul(vector_deviation, inv_covariance_matrix), vector_deviation)
                current_prob = (class_properties[label]['prior'] * math.exp(-0.5 * expt_term)) / denom_term
                class_probabilities[label] = current_prob

            class_probabilities = normalize_probability_weights(class_probabilities)
            log.debug("class_probabilities: " + str(class_probabilities))

            predicted_label = None
            highest_probability = 0
            for label in class_probabilities.keys():
                if class_probabilities[label] > highest_probability:
                    highest_probability = class_probabilities[label]
                    predicted_label = label

            if correct_label == predicted_label:
                accuracy_count += 1

        return accuracy_count / len(test_set_vectors)
