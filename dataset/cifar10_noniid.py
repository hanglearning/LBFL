import numpy as np
from torchvision import datasets, transforms


def get_dataset_cifar10_extr_noniid(n_devices, n_labels, total_samples, alpha, log_dirpath):
    data_dir = './data'
    apply_transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))])
    train_dataset = datasets.CIFAR10(data_dir, train=True, download=True,
                                     transform=apply_transform)

    test_dataset = datasets.CIFAR10(data_dir, train=False, download=True,
                                    transform=apply_transform)

    # Chose equal splits for every user
    user_groups_train, user_groups_test, user_groups_labels = cifar_extr_noniid(
        train_dataset, test_dataset, n_devices, n_labels, total_samples, alpha, log_dirpath)
    return train_dataset, test_dataset, user_groups_train, user_groups_test, user_groups_labels


def cifar_extr_noniid(train_dataset, test_dataset, n_devices, n_labels, num_samples, alpha, log_dirpath):
    num_shards_train, num_imgs_train = int(50000/num_samples), num_samples
    n_labels = 10
    num_imgs_perc_test, num_imgs_test_total = 1000, 10000

    assert(n_labels * n_devices <= num_shards_train)
    assert(n_labels <= n_labels)

    dict_users_train = {i: np.array([]) for i in range(n_devices)}
    dict_users_test = {i: np.array([]) for i in range(n_devices)}
    dict_users_labels = {i: np.array([]) for i in range(n_devices)}
    idxs = np.arange(num_shards_train*num_imgs_train)

    labels = np.array(train_dataset.targets)
    idxs_test = np.arange(num_imgs_test_total)
    labels_test = np.array(test_dataset.targets)

    idxs_labels = np.vstack((idxs, labels))
    idxs_labels = idxs_labels[:, idxs_labels[1, :].argsort()]
    idxs = idxs_labels[0, :]
    labels = idxs_labels[1, :]

    idxs_labels_test = np.vstack((idxs_test, labels_test))
    idxs_labels_test = idxs_labels_test[:, idxs_labels_test[1, :].argsort()]
    idxs_test = idxs_labels_test[0, :]
    labels_test = idxs_labels_test[1, :]

    idxs_train_splits = [[] for i in range(n_labels)]
    for i in range(len(labels)):
        idxs_train_splits[labels[i]].append(np.array(idxs[i])) # append the index of the train sample to the corresponding list of the label of the train sample -> key: label, value: list of indices of samples with that label


    idxs_test_splits = [[] for i in range(n_labels)]
    for i in range(len(labels_test)):
        idxs_test_splits[labels_test[i]].append(np.array(idxs_test[i])) # append the index of the test sample to the corresponding list of the label of the test sample -> key: label, value: list of indices of samples with that label

    for i in range(n_devices):

        # assign training samples
        user_labels = list(set(np.random.choice(10, n_labels, replace=False)))
        dict_users_labels[i] = user_labels
        label_to_qty = {}
        for l_iter, l in enumerate(user_labels):
            all_indices = idxs_train_splits[l] # get all indices of samples with label l
            to_use_alpha = 1 if l_iter == 0 else alpha
            sampled_indices = np.random.choice(len(all_indices), int(num_imgs_train * to_use_alpha), replace=False)
            sampled_elements = np.array(all_indices)[sampled_indices]
            idxs_train_splits[l] = np.delete(idxs_train_splits[l], sampled_indices)
            dict_users_train[i] = np.concatenate(
                    (dict_users_train[i], sampled_elements), axis=0)
            label_to_qty[l] = len(sampled_elements)

        display_text = f"Device {i + 1}  - labels {list(label_to_qty.keys())}, corresponding qty {list(label_to_qty.values())}"
        with open(f'{log_dirpath}/dataset_assigned.txt', 'a') as f:
            f.write(f'{display_text}\n')
        print(display_text)

        for l in user_labels:
            dict_users_test[i] = np.concatenate(
                (dict_users_test[i], idxs_test_splits[int(l)]), axis=0)
    return dict_users_train, dict_users_test, dict_users_labels
