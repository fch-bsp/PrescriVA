from setuptools import setup, find_packages

setup(
    name="prescriva",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.22.0",
        "google-generativeai>=0.3.1",
        "python-dotenv>=1.0.0",
        "opencv-python>=4.7.0.72",
        "pytesseract>=0.3.10",
        "Pillow>=9.5.0",
        "reportlab>=3.6.12",
        "boto3>=1.28.38",
        "numpy>=1.24.3",
    ],
    python_requires=">=3.8",
    author="PrescriVA Team",
    author_email="contato@prescriva.com",
    description="Assistente Virtual para Interpretação de Receitas Médicas",
    keywords="receita, médica, OCR, IA, assistente virtual",
    url="https://github.com/seu-usuario/prescriva",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)