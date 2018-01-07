FROM debian:stable

# Add traffic-ui files
ADD config.ini /
ADD docs/requirements.txt /
ADD inc /inc
ADD traffic_ui /traffic_ui
ADD traffic_ui.py /
ADD views /views

# Create input, cache and store for data
RUN mkdir /input && \
    mkdir /cache && \
    mkdir /store

# Install required dependencies
RUN apt-get update && \
    apt-get install -y python-pip libpcap-dev && \
    pip install -r /requirements.txt

# Expose traffic-ui's port, 8080
EXPOSE 8080

# Launch traffic-ui
CMD ["python", "traffic_ui.py"]
