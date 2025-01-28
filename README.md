# 🌌 Blue Sky Autonomous AI  

An application for generating posts and comments on the **Blue Sky** platform, built on the AT protocol. It leverages agents from the **Autogen framework**. This application was designed with the use of fine-tuned models from the Gandalf series in mind.The dataset was generated using **GPT-4** based on Brock Houston [dataset](https://huggingface.co/datasets/brockhouston/gandalf_therapist) from Hugging Face.

#### Recommended LLMs

- **[DeepSeek-R1-Gandalf](https://huggingface.co/maciejonek/DeepSeek-R1-Gandalf)**
- **[Llama-3.1-8B-Gandalf](https://huggingface.co/maciejonek/Llama-3.1-8B-Gandalf)**
- **[Mistral-7B-Gandalf](https://huggingface.co/maciejonek/Mistral-7b-Gandalf)**
- **[Qwen2.5-7B-Gandalf](https://huggingface.co/maciejonek/Qwen2.5-7B-Gandalf)**
##### Models are available on my Hugging Face repository.

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

### Metrics explanation
- Style Score - Maintains a consistent and appropriate tone, language, and manner that matches the desired character.
- Bleu Score - The quality of generated text by comparing it to reference text. 
- Closure Score - Fully concluded submission, without leaving any unfinished statements.
- Relevance Score - Output aligns with the user input, staying true to context.
- Coherence Score - The submission coherent with received message.
- Generation Time - Represents the time required for the model to generate responses for the testing dataset. 

## 📝 License  

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

