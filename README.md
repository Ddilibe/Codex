# Project Name

## Table of Contents

- [Project Name](#project-name)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Installation](#installation)
  - [Usage](#usage)
  - [License](#license)

## Description
Codex is an innovative and comprehensive digital library project that transcends the boundaries of traditional libraries, inviting users into a realm where ancient wisdom, literary treasures, and the wonders of knowledge converge. This digital sanctuary is meticulously curated to provide a unique and immersive reading experience, reminiscent of the grandeur of medieval times.


## Installation

1. Clone the repository:

```bash
git clone https://github.com/ddilibe/codex.git
cd codex
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Apply migrations (if applicable):

```bash
python manage.py migrate
```

5. Start the redis server

```bash
redis-server
```

6. Start the celery server 

```bash
celery -A core worker -l info
```

7. Run the development server:

```bash
python manage.py runserver
```

1. Open your browser and visit <http://localhost:8000/>.

## Usage

Explain how to use your project. Provide examples and any necessary instructions.

## License


This project is licensed under the MIT License
