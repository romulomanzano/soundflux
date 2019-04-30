#create the folder where the model details will go
mkdir ~/soundflux_models
mkdir ~/soundflux_models/latest
wget https://s3.amazonaws.com/soundflux-urbansounds/soundflux_latest_model.zip -P ~/soundflux_models/latest
unzip ~/soundflux_models/latest/soundflux_latest_model.zip -d ~/soundflux_models/latest
#create .env file
touch ~/github/soundflux/.env
#add model meta
echo "SOUNDFLUX_MODEL_WEIGHTS_LOCATION='/home/pi/soundflux_models/latest/soundflux_latest_model.h5'" >> ~/github/soundflux/.env
echo "SOUNDFLUX_MODEL_DEFINITION_LOCATION='/home/pi/soundflux_models/latest/soundflux_latest_model.json'" >> ~/github/soundflux/.env
echo "SOUNDFLUX_MODEL_LABELS_MAP_LOCATION='/home/pi/soundflux_models/latest/soundflux_latest_model_class_indices.json'" >> ~/github/soundflux/.env