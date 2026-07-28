import numpy as np

X_COLUMN, Y_COLUMN, TIMESTAMP_COLUMN, POLARITY_COLUMN = range(4)


def load_events(filename, bsergb=False, size=None):
    data = np.load(filename, allow_pickle=True)
    if bsergb:
        x = (2 * 970 * data['x'].astype(np.float64).reshape(-1)) // 62000
        y = (630 * data['y'].astype(np.float64).reshape(-1)) // 20160
        timestamp = data['timestamp'].astype(np.float64).reshape(-1)
        polarity = data['polarity'].astype(np.float32).reshape(-1) * 2 - 1
    else:
        x = data['x'].astype(np.float32).reshape(-1)
        y = data['y'].astype(np.float32).reshape(-1)
        timestamp = data['t'].astype(np.float32).reshape(-1)
        polarity = data['p'].astype(np.float32).reshape(-1)
    events = np.stack((x, y, timestamp, polarity), axis=-1)
    if size is not None:
        top, left, bottom, right = size
        valid = ((events[:, X_COLUMN] >= left) & (events[:, X_COLUMN] < right) &
                 (events[:, Y_COLUMN] >= top) & (events[:, Y_COLUMN] < bottom))
        events = events[valid]
        events[:, X_COLUMN] -= left
        events[:, Y_COLUMN] -= top
    return events


class EventSequence:
    def __init__(self, features, image_height, image_width):
        self._features = features
        self._image_height = image_height
        self._image_width = image_width
        self._start_time = features[0, TIMESTAMP_COLUMN]
        self._end_time = features[-1, TIMESTAMP_COLUMN]

    def __len__(self):
        return len(self._features)

    def start_time(self):
        return self._start_time

    def end_time(self):
        return self._end_time

    def duration(self):
        return self._end_time - self._start_time

    def reverse(self):
        features = self._features.copy()
        features[:, TIMESTAMP_COLUMN] = self._end_time - features[:, TIMESTAMP_COLUMN]
        features[:, POLARITY_COLUMN] *= -1
        return EventSequence(np.flipud(features).copy(), self._image_height, self._image_width)

    @classmethod
    def from_npz_files(cls, filenames, image_height, image_width, bsergb=False, size=None):
        features = [load_events(filename, bsergb=bsergb, size=size) for filename in filenames]
        return cls(np.concatenate(features), image_height, image_width)
