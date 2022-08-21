## <div align="center"> Automated Image Crawler </div>
<p>
   <img width="850" src="./automated crawler.jpg"></a>
</p>

## <div align="center">Documentation</div>

It is a simple image crawler with Selenium, but its differentiation is that it can detect objects in an image with a customized pre-trained model (Yolov5) and improve the model's performance using crawled images.
<p># I used it to crawl anus diseases images.</p>

<details open>
<summary>Used Skills</summary>
- Cloud: AWS S3, EC2, RDS (PostgreSQL) </br>
- Container: Docker, Docekr Compose </br>
- CI/CD: GitHub Action, AWS CodeDeploy </br>
- Automation: Airflow </br>
</details>

<details open>
<summary>Install</summary>

Clone repo and install requirements.txt
```bash
git clone https://github.com/farmboy-dev/Anus  # clone
pip install -r requirements.txt  # install
```

</details>

<details open>
<summary>Collector</summary>
If the object is detected -> Crawl the image

```bash
# at Anus
python ./yolov5/image_collector.py
```
</details>

<details>
<summary>Verifier</summary>
The customized pre-trained model is not perfect, so sometime it detects a wrong object. That is reason why I made the verifier to feed good quality images to the model.

```bash
# at Anus
python ./yolov5/image_verifier.py
```
</details>

<details>
<summary>Cropper</summary>
My purpose is to detect anus disease (object) and crop the object not whole image.

```bash
# at Anus
python ./yolov5/image_cropper.py
```
</details>

### <div align="Center"> Further Tasks </div>
1. Data Version Control
2. Tracking a status of models (performace, reproducibility, etc)