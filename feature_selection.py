import time
import numpy as np
import pandas as pd
import re

class FeatureSelection:
    def __init__(self, dataset):
        self.dataset = dataset
        self.data = pd.read_csv(dataset, header=None, sep=r"\s+")


    def cross_validation(self, complete_data, cur_features, feat_to_add):
        # Perform cross-validation by leaving one instance out and evaluating accuracy
        data = np.copy(complete_data)

        # Set non-selected features (except the one to add) to zero
        i = 1
        while i < complete_data.shape[1]:
            if i not in cur_features and i != feat_to_add:
                data[:, i] = 0
            i += 1

        num_correct, num_rows = 0, data.shape[0]
        i = 0
        while i < num_rows:
            objs_to_classify = data[i, 1:]
            label = data[i, 0]

            # Find the nearest neighbor
            nn_loc = float('inf')
            nn_dist = float('inf')
            nn_lbl = 0.0

            j = 0
            while j < num_rows:
                if i != j:
                    dist = np.sqrt(np.sum(np.square(objs_to_classify - data[j, 1:]))) # Calculating Euclidean Distance
                    if dist <= nn_dist:
                        nn_dist, nn_loc = dist, j
                        nn_lbl = data[nn_loc, 0]
                j += 1

            # Check if the label of the nearest neighbor matches the actual label
            if label == nn_lbl:
                num_correct += 1
            i += 1

        acc = num_correct / num_rows
        return acc
    


    def forward_selection(self):
        # Perform forward feature selection
        current_features = set()
        feature_performances = {}
        accuracies = set()
        highest_accuracy = 0

        num_cols = self.data.shape[1]
        num_instances = self.data.shape[0]
        # Print dataset information
        if flag:
            print("\nThis dataset has {} features (not including the class attribute), with {} random instances".format(num_cols - 1, num_instances))
        else:
            print("\nThis dataset has {} features (not including the class attribute), with {} instances".format(num_cols - 1, num_instances))
        print("\nRunning nearest neighbor with all {{}} features, using 'leaving-one-out' evaluation, I get an accuracy of {:.1f}%\n".format(self.cross_validation(self.data, set(), 0) * 100))
        print("\nBeginning search")

        for i in range(num_cols - 1):
            feature_to_add = None
            best_accuracy = 0
            selected_features = current_features.copy()

            print('Evaluating level {} of the search tree'.format(i + 1))

            for j in range(num_cols - 1):
                if j + 1 not in current_features:
                    # Evaluate the accuracy with the added feature
                    accuracy = self.cross_validation(self.data, current_features, j + 1)
                    print('\t Using feature(s) {} accuracy is {}%'.format(selected_features.union({j + 1}), round(accuracy * 100, 1)))

                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        feature_to_add = j + 1

                    accuracies.add(round(best_accuracy, 3))

            if best_accuracy < highest_accuracy:
                print('\n(Warning, Accuracy has decreased! Continuing search in case of local maxima)')

            highest_accuracy = max(highest_accuracy, best_accuracy)

            current_features.add(feature_to_add)
            selected_features.add(feature_to_add)
            rounded_accuracy = round(best_accuracy, 3)
            if rounded_accuracy not in feature_performances.keys():
                feature_performances[rounded_accuracy] = selected_features.copy()

            print('Feature set {} was best, accuracy is {}%'.format(selected_features, round(best_accuracy * 100, 1)))
            print()

        print('Finished search!! The best feature subset is {}, which has an accuracy of {}%'.format(
            feature_performances[max(accuracies)], round(max(accuracies) * 100, 1)))

        return accuracies, feature_performances




    def backward_elimination(self):
        # Perform Backward elimination
        current_features = set(range(1, self.data.shape[1]))
        feature_performances = {}
        accuracies = set()
        highest_accuracy = 0

        num_cols = self.data.shape[1]
        num_instances = self.data.shape[0]

        # Print dataset information
        print("\nThis dataset has {} features (not including the class attribute), with {} instances".format(num_cols - 1, num_instances))
        print("\nRunning nearest neighbor with all {} features, using 'leaving-one-out' evaluation, I get an accuracy of {:.1f}%\n".format(num_cols - 1, self.cross_validation(self.data, current_features, 0) * 100))
        print("\nBeginning search")

        for i in range(num_cols - 1):
            feature_to_remove = None
            best_accuracy = 0
            selected_features = current_features.copy()

            print('Evaluating level {} of the search tree'.format(i + 1))

            for j in range(num_cols - 1):
                if j + 1 in current_features:
                    sub_features = current_features.copy()
                    sub_features.remove(j + 1)
                    # Evaluate the accuracy with the feature removed
                    accuracy = self.cross_validation(self.data, sub_features, 0)

                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        feature_to_remove = j + 1

                    accuracies.add(best_accuracy)
                    print('\tUsing feature(s) {} accuracy is {}%'.format(selected_features - {j + 1}, round(accuracy * 100, 1)))

            if best_accuracy < highest_accuracy:
                print('\n(Warning, Accuracy has decreased! Continuing search in case of local maxima)')

            highest_accuracy = max(highest_accuracy, best_accuracy)

            current_features.remove(feature_to_remove)
            rounded_accuracy = round(best_accuracy, 3)
            if rounded_accuracy not in feature_performances.keys():
                feature_performances[rounded_accuracy] = current_features.copy()

            print('Feature {} removed on level {}'.format(feature_to_remove, i + 1))
            if i < num_cols - 2:
                print('Feature set {} was best, accuracy is {}%'.format(selected_features - {feature_to_remove}, round(best_accuracy * 100, 1)))
                print()

        if num_cols > 2:
            last_accuracy = max(accuracies)
            last_feature_set = feature_performances.get(round(last_accuracy, 3))

            if last_feature_set is not None:
                print('Feature set {} was best, accuracy is {}%'.format(last_feature_set, round(last_accuracy * 100, 1)))
                print()

        print('Finished search!! The best feature subset is {}, which has an accuracy of {}%'.format(
            feature_performances.get(round(max(accuracies), 3)), round(max(accuracies) * 100, 1)))


        return accuracies, feature_performances


    def run_feature_selection(self):
        # Prompt the user to choose between forward selection and backward elimination
        print('Type the number of the algorithm you want to run: \n')
        user_input = int(input("1. Forward Selection\n2. Backward Elimination\nEnter 1 or 2: "))

        if user_input == 1:
            self.forward_selection()
        else:
            self.backward_elimination()

    def main(self):
        # Main function to run the feature selection algorithm
        start_time = time.time()
        if re.search('.*XXXlarge.*', dataset):    # If the filename has XXXlarge
            np.random.seed(42)  # Set the random seed for reproducibility
            self.data = self.data.to_numpy()
            np.random.shuffle(self.data)
            random_rows = np.random.choice(np.arange(self.data.shape[0]), size=100, replace=False) # Set the instance size
            self.data = self.data[random_rows, :]
            global flag
            flag = True
            self.run_feature_selection()
        else:
            self.run_feature_selection()
        end_time = time.time()
        time_elapsed = end_time - start_time
        print("Time elapsed (in secs): ", round(time_elapsed, 3))

global flag     # Adding so that to perform sampling on XXXlarge files
flag = False    # Initializing it to False
dataset = input("Type in the name of the file to test: ")
feature_selection = FeatureSelection(dataset)
feature_selection.main()