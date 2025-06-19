# Contributing to SeismoWatch

Thank you for your interest in contributing to SeismoWatch! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** when available
3. **Provide detailed information** including:
   - Operating system and Python version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Error messages or logs

### Suggesting Features

1. **Check the roadmap** to see if it's already planned
2. **Open a feature request** with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approaches

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes** following our coding standards
4. **Write tests** for new functionality
5. **Run the test suite**:
   ```bash
   pytest
   ```
6. **Submit a pull request**

## 🔧 Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/yourusername/seismowatch.git
cd seismowatch

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to ensure everything works
pytest
```

## 📝 Coding Standards

### Python Style

- Follow **PEP 8** style guidelines
- Use **Black** for code formatting
- Use **type hints** where appropriate
- Write **docstrings** for all public functions and classes

### Code Quality

- **Maximum line length**: 88 characters (Black default)
- **Import sorting**: Use isort
- **Linting**: Code must pass flake8 checks
- **Type checking**: Use mypy for static type analysis

### Running Quality Checks

```bash
# Format code
black seismowatch/ tests/

# Sort imports
isort seismowatch/ tests/

# Lint code
flake8 seismowatch/ tests/

# Type checking
mypy seismowatch/

# Run all checks
pre-commit run --all-files
```

## 🧪 Testing

### Writing Tests

- Write tests for all new functionality
- Use **pytest** for testing framework
- Aim for **high test coverage** (>90%)
- Include both **unit tests** and **integration tests**

### Test Categories

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **API tests**: Test web endpoints
- **CLI tests**: Test command-line interface

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=seismowatch

# Run specific test file
pytest tests/test_earthquakes.py

# Run tests matching pattern
pytest -k "test_earthquake"
```

## 📚 Documentation

### Code Documentation

- Write clear **docstrings** using Google style
- Include **examples** in docstrings when helpful
- Document **parameters**, **returns**, and **raises**

### User Documentation

- Update **README.md** for new features
- Add **examples** to documentation
- Update **API documentation** for endpoint changes

## 🚀 Pull Request Process

### Before Submitting

1. **Rebase** your branch on the latest main
2. **Run all tests** and ensure they pass
3. **Update documentation** as needed
4. **Add changelog entry** if applicable

### PR Description

Include in your pull request:

- **Clear description** of changes
- **Motivation** for the changes
- **Testing** performed
- **Screenshots** for UI changes
- **Breaking changes** if any

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Address feedback** promptly
4. **Squash commits** if requested

## 🗺️ Project Structure

```
seismowatch/
├── seismowatch/           # Main package
│   ├── __init__.py       # Package initialization
│   ├── cli.py           # Command line interface
│   ├── earthquakes.py   # Earthquake data handling
│   ├── alerts.py        # Alert system
│   ├── geo.py          # Geospatial utilities
│   ├── web.py          # Web application
│   └── dashboard.py    # Real-time dashboard
├── tests/               # Test suite
│   ├── test_earthquakes.py
│   ├── test_alerts.py
│   └── test_web.py
├── scripts/             # Build and utility scripts
├── docs/               # Documentation
└── .github/            # GitHub workflows
```

## 🌟 Recognition

Contributors will be:

- **Listed** in the README contributors section
- **Credited** in release notes for significant contributions
- **Invited** to join the core team for sustained contributions

## 📞 Getting Help

- **Discord**: Join our [Discord server](https://discord.gg/seismowatch)
- **GitHub Discussions**: Use for general questions
- **Email**: Contact maintainers at contributors@seismowatch.dev

## 📋 Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## 🎯 Priorities

Current priority areas for contributions:

1. **Performance improvements** for large datasets
2. **Mobile app** development
3. **Additional data sources** integration
4. **Machine learning** for earthquake prediction
5. **Internationalization** and localization

Thank you for contributing to SeismoWatch! 🌍