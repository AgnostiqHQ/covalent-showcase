# Real-Time Image Generator: SDXL

<div align="center">
<img src="./assets/streamlit-sdxl-demo.gif">
</div>

## Instructions

To try this out, you can run a local Streamlit application that generates images in real-time using the SDXL model hosted on a Covalent service.

1. Make a conda environment with:
```
covalent-cloud>=0.65.1
streamlit==1.35.0
torch==2.2.2
transformers==4.39.3
diffusers==0.27.2
```

2. Run the `sdxl-backend.ipynb` notebook to deploy the GPU Backend with Covalent.

3. Run the command `streamlit run sdxl-frontend.py` to start the local Streamlit app.

4. Copy-paste the deployment address and API key into the app's "Settings" sidebar.

That's all. You can now generate images in real-time with the SDXL model!

## Details

This example runs the following pipeline using a GPU-equipped backend via Covalent Cloud.

```python
pipeline = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sdxl-turbo",
    torch_dtype=torch.float16,
    variant="fp16",
).to("cuda")
```