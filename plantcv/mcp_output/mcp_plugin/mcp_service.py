import os
import sys
from typing import Dict, Any, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from plantcv import plantcv as pcv
from plantcv.parallel import inspect_dataset, job_builder, multiprocess, process_results, workflow_inputs
from plantcv.learn import naive_bayes as learn_naive_bayes
from plantcv.learn import train_kmeans as learn_train_kmeans
from plantcv.utils import converters as utils_converters

mcp = FastMCP("plantcv_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="pcv_read_image", description="Read an image from disk using PlantCV.")
def pcv_read_image(filename: str, mode: str = "native") -> Dict[str, Any]:
    """
    Read an image from disk.

    Parameters:
        filename: Path to image file.
        mode: Read mode ('native', 'rgb', etc., depending on PlantCV/OpenCV behavior).

    Returns:
        Dictionary with success/result/error where result contains image shape metadata.
    """
    try:
        img, _, _ = pcv.readimage(filename=filename, mode=mode)
        return _ok({"shape": tuple(img.shape)})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="pcv_rgb2gray", description="Convert RGB image to grayscale channel.")
def pcv_rgb2gray(filename: str, channel: str = "v") -> Dict[str, Any]:
    """
    Convert an input RGB image to grayscale via selected color-space channel.

    Parameters:
        filename: Path to image file.
        channel: One of supported channel names in PlantCV rgb2gray (e.g., 'r','g','b','l','a','b','h','s','v').

    Returns:
        Dictionary with success/result/error including output shape.
    """
    try:
        img, _, _ = pcv.readimage(filename=filename, mode="rgb")
        gray = pcv.rgb2gray(rgb_img=img, channel=channel)
        return _ok({"shape": tuple(gray.shape)})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="pcv_threshold_binary", description="Apply binary threshold to an image.")
def pcv_threshold_binary(filename: str, threshold: int, max_value: int = 255, object_type: str = "light") -> Dict[str, Any]:
    """
    Apply binary thresholding to a grayscale image.

    Parameters:
        filename: Path to image file.
        threshold: Threshold value.
        max_value: Max output value for threshold.
        object_type: 'light' or 'dark'.

    Returns:
        Dictionary with success/result/error including mask shape.
    """
    try:
        img, _, _ = pcv.readimage(filename=filename, mode="gray")
        mask = pcv.threshold.binary(gray_img=img, threshold=threshold, max_value=max_value, object_type=object_type)
        return _ok({"shape": tuple(mask.shape)})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="pcv_find_objects", description="Find objects/contours in a mask.")
def pcv_find_objects(filename: str, threshold: int = 127) -> Dict[str, Any]:
    """
    Detect contours from a thresholded image.

    Parameters:
        filename: Path to image file.
        threshold: Binary threshold to generate mask before contour extraction.

    Returns:
        Dictionary with success/result/error including contour count.
    """
    try:
        img, _, _ = pcv.readimage(filename=filename, mode="gray")
        mask = pcv.threshold.binary(gray_img=img, threshold=threshold, max_value=255, object_type="light")
        contours, hierarchy = pcv.find_objects(img=mask, mask=mask)
        return _ok({"contours": len(contours), "hierarchy_found": hierarchy is not None})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="pcv_analyze_size", description="Analyze object size metrics from mask.")
def pcv_analyze_size(filename: str, threshold: int = 127, label: str = "default") -> Dict[str, Any]:
    """
    Run size analysis on segmented objects.

    Parameters:
        filename: Path to image file.
        threshold: Threshold used to create binary mask.
        label: Label for analysis run.

    Returns:
        Dictionary with success/result/error including whether analysis executed.
    """
    try:
        img, _, _ = pcv.readimage(filename=filename, mode="rgb")
        gray = pcv.rgb2gray(rgb_img=img, channel="v")
        mask = pcv.threshold.binary(gray_img=gray, threshold=threshold, max_value=255, object_type="light")
        _ = pcv.analyze.size(img=img, labeled_mask=mask, n_labels=1, label=label)
        return _ok("analyze.size completed")
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="parallel_inspect_dataset", description="Inspect dataset metadata for parallel workflows.")
def parallel_inspect_dataset(metadata_file: str) -> Dict[str, Any]:
    """
    Inspect dataset metadata used by PlantCV parallel pipeline.

    Parameters:
        metadata_file: Path to metadata JSON file.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        result = inspect_dataset.main(metadata=metadata_file)
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="parallel_build_jobs", description="Build parallel job files from workflow config.")
def parallel_build_jobs(config_file: str, outdir: str) -> Dict[str, Any]:
    """
    Build job definitions for PlantCV parallel execution.

    Parameters:
        config_file: Path to workflow config JSON.
        outdir: Output directory for generated job files.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        result = job_builder.main(config=config_file, outdir=outdir)
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="parallel_run_multiprocess", description="Run PlantCV parallel multiprocess jobs.")
def parallel_run_multiprocess(job_dir: str, cpu: int = 1) -> Dict[str, Any]:
    """
    Execute parallel jobs through PlantCV multiprocess runner.

    Parameters:
        job_dir: Directory containing job files.
        cpu: Number of worker processes.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        result = multiprocess.main(job_dir=job_dir, cpu=cpu)
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="parallel_process_results", description="Aggregate and process PlantCV parallel results.")
def parallel_process_results_tool(results_dir: str, outdir: str) -> Dict[str, Any]:
    """
    Process parallel job outputs into consolidated results.

    Parameters:
        results_dir: Directory with per-job output files.
        outdir: Output directory for merged results.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        result = process_results.main(results=results_dir, outdir=outdir)
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="parallel_parse_workflow_inputs", description="Parse workflow input metadata into task lists.")
def parallel_parse_workflow_inputs(metadata_file: str, input_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse workflow inputs for PlantCV parallel processing.

    Parameters:
        metadata_file: Path to metadata JSON.
        input_dir: Optional input directory override.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        result = workflow_inputs.main(metadata=metadata_file, input_dir=input_dir)
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="learn_train_naive_bayes", description="Train a naive Bayes model using PlantCV learn module.")
def learn_train_naive_bayes(pdf_file: str, output_model: str) -> Dict[str, Any]:
    """
    Train PlantCV naive Bayes model.

    Parameters:
        pdf_file: Path to class PDF definitions.
        output_model: Destination path for trained model output.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        result = learn_naive_bayes.naive_bayes_train(pdf_file=pdf_file, out_file=output_model)
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="learn_train_kmeans", description="Train K-means clustering model using PlantCV learn module.")
def learn_train_kmeans_tool(image_paths: List[str], k: int, output_model: str) -> Dict[str, Any]:
    """
    Train a K-means model from a list of images.

    Parameters:
        image_paths: List of input image paths.
        k: Number of clusters.
        output_model: Output file path for model.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        result = learn_train_kmeans.train_kmeans(images=image_paths, k=k, out_file=output_model)
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="utils_json_to_csv", description="Convert PlantCV JSON results to CSV.")
def utils_json_to_csv(json_file: str, csv_file: str) -> Dict[str, Any]:
    """
    Convert PlantCV output JSON into CSV.

    Parameters:
        json_file: Input JSON file path.
        csv_file: Output CSV file path.

    Returns:
        Dictionary with success/result/error.
    """
    try:
        result = utils_converters.json2csv(json_file=json_file, csv_file=csv_file)
        return _ok(result)
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()