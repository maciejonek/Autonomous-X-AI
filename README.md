# 🌌 Blue Sky Autonomous AI  

An application for generating posts and comments on the **Blue Sky** platform, built on the AT protocol. It leverages agents from the **Autogen framework**.  
The dataset was generated using **GPT-4** based on another dataset [link].  

## 📥 Installation  

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required packages:  

```bash
pip install -r /path/to/requirements.txt
```

## 🚀 Usage  

Run the application using the following command:  

```python
python gradio_interface.py
```

## 📊 Metrics  

The evaluation metrics were derived using the `evaluation.py` script.  

| Model                     | Style Score | Bleu Score | Closure Score | Relevance Score | Coherence Score | Generation Time |
|---------------------------|-------------|------------|---------------|-----------------|-----------------|-----------------|
| DeepSeek-R1-Gandalf       | 0.88        | 0.071      | 0.48          | 0.24            | 0.84            | 66.36s          |
| Qwen2.5-7B-Gandalf        | 0.92        | 0.068      | 0.64          | 0.4             | 0.88            | 59.25s          |
| Llama-3.1-8B-Gandalf      | 0.96        | 0.088      | 0.48          | 0.4             | 0.72            | 66.67s          |
| Mistral-7B-Gandalf        | 0.92        | 0.089      | 0.56          | 0.4             | 0.8             | 59.69s          |
| Qwen2.5-7B-Instruct-MLX-4bit | 0.88    | 0.023      | 0.04          | 0.92            | 0.96            | 101.97s         |

## 📝 License  

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

