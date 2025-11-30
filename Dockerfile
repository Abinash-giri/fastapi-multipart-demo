FROM public.ecr.aws/lambda/python:3.10

WORKDIR /var/task

COPY pyproject.toml poetry.lock* ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-root

COPY app app

CMD ["app.main.handler"]
