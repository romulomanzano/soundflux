# What Goes Here
This folder will hold all the necessary details to launch a web server that centralizes
communication and account management for SoundFlux.

#Todos:

- Develop a single flask app to act as the API
- Create classes via mongo orm that support the basic back-end structure
- Move the communications module to this app (out of the larger SoundFlux folder)

# Data Model:

Classes listed below

- Account
    - email address
- Device
    - id
    - account_id
- Samples:
    - type: train or test
    - device_id
    - date
    - account_id
    - img_url (s3bucketimage)
    - label
    - predicted_class_a
    - predicted_class_a_proba
    - predicted_class_b
    - predicted_class_b_proba
     
For v1 of this project, we'll make an inefficient decision given we've built a single page web app using firebase.
We'll write the sample data to the local mongodb and push the data to Firebase as well.

The img data will be stored in S3, not locally. Only the s3 bucket links will be made available