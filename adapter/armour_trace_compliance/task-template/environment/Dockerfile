FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ARMOUR_STATE_DIR=/var/lib/armour

COPY . /opt/armour-task
RUN chmod +x /opt/armour-task/armour_tool.py \
    && ln -s /opt/armour-task/armour_tool.py /usr/local/bin/armour-tool \
    && mkdir -p /var/lib/armour /workspace \
    && PYTHONPATH=/opt/armour-task python3 -c "from pathlib import Path; from armour_tool import MockToolEnvironment, load_scenario; scenario = load_scenario(); MockToolEnvironment(scenario, Path('/var/lib/armour')).reset(session_id=scenario['task_id'])"

WORKDIR /workspace

CMD ["bash"]
