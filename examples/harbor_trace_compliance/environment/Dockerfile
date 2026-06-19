FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ARMOUR_STATE_DIR=/var/lib/armour

COPY . /opt/armour-environment
RUN chmod +x /opt/armour-environment/armour_tool.py \
    && ln -s /opt/armour-environment/armour_tool.py /usr/local/bin/armour-tool \
    && mkdir -p /var/lib/armour /workspace \
    && PYTHONPATH=/opt/armour-environment python3 -c "from pathlib import Path; from armour_tool import MockCustomerService; MockCustomerService(Path('/var/lib/armour')).reset(session_id='harbor-customer-ticket')"

WORKDIR /workspace

CMD ["bash"]
