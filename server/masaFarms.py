import prepare_data
import collect_forecast
import predict

def run():
    prepare_data.run()
    collect_forecast.run()
    predict.predict()

run()