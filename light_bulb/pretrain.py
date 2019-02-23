import plac
import yaml
import pdb
import os
import pandas as pd

from labels.label import Label
from utils.config_parser import ConfigParser
from dataset import JSONDataset, TextDataset
from label_app import Task, LabelApp
from dataset import Dataset
from labels.label import Label

class PretrainJSONDataset(JSONDataset):
    COLUMNS = ['label', 'text']

    def load_existing_judgements(self):
        df = pd.read_csv(self.judgements_file)
        assert sorted(df.columns) == sorted(self.__class__.COLUMNS)
        df['labelled'] = True
        df['time_taken'] = 0
        df['stage'] = Dataset.TRAIN
        return df

    # Don't load anything unlabeled
    def load_unlabelled_dataset(self):
        pass

class PretrainTextDataset(TextDataset):
    COLUMNS = ['label', 'text']

    def load_existing_judgements(self):
        df = pd.read_csv(self.judgements_file)
        assert sorted(df.columns) == sorted(self.__class__.COLUMNS)
        df['labelled'] = True
        df['time_taken'] = 0
        df['stage'] = Dataset.TRAIN
        return df

    # Don't load anything unlabeled
    def load_unlabelled_dataset(self):
        pass

@plac.annotations(
    config_path=("Config path.", "option", "c", str),
    epochs=("Num epochs.", "option", "e", int))
def main(config_path, epochs=3):
    # For pretraining, we do everything the same, except we replace the
    # dataset:judgements_file with model:pretrain_file.
    with open(config_path) as f:
        config = yaml.load(f)
        parser = ConfigParser(config)
        parser.dataset['judgements_file'] = parser.model['pretrain_file']

    task = Task.load_from(parser.task)
    dataset = PretrainJSONDataset(parser.dataset)
    model_config = config['model']
    label_helper = Label.load_from(parser.label)
    user = config['user']
    label_app = LabelApp(task, dataset, label_helper, user, model_config, parser)
    label_app.trainer.load_existing()
    label_app.trainer.train_epochs(epochs=epochs)

    # Save the model once its trained

if __name__ == "__main__":
    plac.call(main)
