# Eunomia

Eunomia, the ancient Greek goddess of order and lawful governance, embodies the transformation of chaos into clarity. She brings structure to disarray, ensuring precision, balance, and consistency. A core service that orchestrates the normalization of raw data into clean, reliable models, enforcing standards, validating integrity, and enabling harmony across all ecosystem.

## 📋 Requirements

- Docker
- RabbitMQ
- S3

## 🚀 Build and run

This project is not ment to be run in standalone mode as it has multiple service dependencies.

Before running the worker, make sure Docker is installed and running.

If the worker needs RabbitMQ, both containers should run in the same Docker network.

Build the image

```bash
docker build -t eunomia-worker .
```

Run the container

```bash
docker run --name eunomia-worker -v "$(pwd)":/app -t eunomia-worker
```

## 🧑‍💻 Code quality

We use Ruff for mantaining the code quality. Run the following commands inside the container before commiting:

```bash
ruff check
ruff format
```

## License

Licensed under LGPL-2.1. See [LICENSE](./LICENSE) and [NOTICE](./NOTICE.md) for details.
