<a href="https://github.com/bibek-cse/bibek-cse">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/bibek-cse/bibek-cse/main/dark_mode.svg">
    <img alt="Forensic report card for Bibek Das: research scholar at IIT Patna working on watermarking, provenance and deepfake detection" src="https://raw.githubusercontent.com/bibek-cse/bibek-cse/main/light_mode.svg">
  </picture>
</a>

<p align="center">
  <a href="https://in.linkedin.com/in/bibek6612"><img src="https://img.shields.io/badge/LinkedIn-bibek6612-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
  <a href="https://www.kaggle.com/bibekcse"><img src="https://img.shields.io/badge/Kaggle-bibekcse-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white" alt="Kaggle"/></a>
  <a href="mailto:bibekdas.cse@gmail.com"><img src="https://img.shields.io/badge/Email-bibekdas.cse-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/></a>
  <img src="https://komarev.com/ghpvc/?username=bibek-cse&style=for-the-badge&color=30363d&label=pixels+inspected" alt="Profile views"/>
</p>

<p align="center"><b>I make images and videos verifiable, and I catch them when they aren't.</b><br/>
<sub>Research Scholar · CSE · IIT Patna · computer vision &amp; media forensics</sub></p>

---

### 🗂️ Case files

| | Line of inquiry | What I'm asking |
|:-:|---|---|
| 🛡️ | **Provenance** | Can a watermark survive compression, editing, and an adversary trying to remove it? Who made this image? |
| 🕵️ | **Forensics** | Is this face real? *Where* exactly was this image changed, and can the model show why it thinks so? |
| 🧠 | **Vision-language** | How far can VLMs go zero-shot as detectors and counters, and where do they fail? |

📄 Publishing at **ICPR**, **ICONIP** and **IEEE TBIOM**.

### 🧾 Exhibits

| Exhibit | | |
|:-:|---|---|
| **A** | [**Watermark_Attack**](https://github.com/bibek-cse/Watermark_Attack) | A toolkit of traditional and learning-based attacks for stress-testing image watermarks |
| **B** | [**Deepfake_Detection**](https://github.com/bibek-cse/Deepfake_Detection) | Deepfake detection experiments and pipelines |
| **C** | [**VisionCrowdTest**](https://github.com/bibek-cse/VisionCrowdTest) | Benchmarking vision-language models for zero-shot crowd counting |
| **D** | [**AI GATE Quest**](https://bibek-cse.github.io/ai-gate-quest/) | A game that teaches ML, DL, LLMs, DSA and maths for AI one question at a time |
| **E** | [**Image Edit Studio**](https://github.com/bibek-cse/image-edit-studio) | A free browser front-end for open image-editing models (Qwen-Image-Edit, FLUX Kontext, SDXL) |

### 🎭 Two truths and a deepfake

1. I teach Java & DSA labs, and I turn the lab quizzes into games for my students.
2. The ASCII portrait in the card above was generated from a real photo.
3. I once trained a detector so good it flagged my own selfie as fake.

<details>
<summary><b>Reveal the deepfake</b></summary>
<br/>

**#3 is the fake.** My detectors still think I'm real (`face_0 · REAL · 0.997`). The other two are true.
</details>

### 🔍 Watermark challenge

The card at the top carries a **40-bit invisible watermark**, the same idea I work on, scaled down to something you can decode by hand.

<details>
<summary><b>Hint</b></summary>
<br/>

Open the raw SVG and look along its bottom edge. There are 40 cells: a cell that's present is a <code>1</code> and a gap is a <code>0</code>. Read them MSB first, 8 bits per ASCII character.
</details>

<details>
<summary><b>Solution</b></summary>
<br/>

```python
import re, requests
svg = requests.get("https://raw.githubusercontent.com/bibek-cse/bibek-cse/main/dark_mode.svg").text
wm  = svg.split('<g id="wm"')[1].split("</g>")[0]
x0, bits = (985 - 240) // 2, ["0"] * 40
for x in map(int, re.findall(r'x="(\d+)"', wm)):
    bits[(x - x0) // 6] = "1"
b = "".join(bits)
print("".join(chr(int(b[i:i + 8], 2)) for i in range(0, 40, 8)))
```
</details>

### 🛠️ Lab equipment

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white" alt="Java"/>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch"/>
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white" alt="OpenCV"/>
  <img src="https://img.shields.io/badge/Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="Hugging Face"/>
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white" alt="Jupyter"/>
  <img src="https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black" alt="Linux"/>
  <img src="https://img.shields.io/badge/HPC-Param%20Rudra-2E3440?style=flat-square&logo=linux&logoColor=white" alt="HPC"/>
</p>

---

<p align="center"><sub><i>"Your work reflects your character."</i> · verdict: <b>authentic</b></sub></p>
