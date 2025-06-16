import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

data_dict = pickle.load(open("dataforgame.pickle", "rb"))
raw_data = data_dict['dataforgame']
raw_labels = data_dict['labels']  # or whatever the correct key is

# Filter both together
data = []
labels = []

for d, l in zip(raw_data, raw_labels):
    if len(d) >= 42:
        data.append(d[:42])  # trim to 42 if needed
        labels.append(l)

# Convert to numpy arrays
data = np.asarray(data)
labels = np.asarray(labels)

x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

model = RandomForestClassifier()
model.fit(x_train, y_train)

y_pred = model.predict(x_test)

score = accuracy_score(y_pred, y_test)
print('{}% of samples are correct'.format(score*100))

f = open('modelforgame.p', 'wb')
pickle.dump({'model' : model}, f)
f.close()