import time
import subprocess
from typing import Optional, List


def image_lookup(repository: str) -> List[str]:
    """
    Given an imagen path, searches and returns a list of its direct children
    """
    gcloud_list_cmd = (
        lambda repo: "gcloud container images list "
        f"--repository={repo} --format=get(name)"
    )
    split_gcloud_list_cmd = gcloud_list_cmd(repo=repository)

    run_gcloud = subprocess.run(
        split_gcloud_list_cmd, capture_output=True, text=True
    ).stdout
    process_output = list(filter(lambda x: len(x) > 1), run_gcloud.split("\n"))

    return process_output


def get_untagged_images(image_repo_path: str) -> Optional[List[str]]:
    """
    Given an image path, return all untagged versions of that image
    """

    gcloud_untagged_cmd = [
        "gcloud",
        "container",
        "images",
        "list-tags",
        image_repo_path,
        "--format=get(digest)",
        "--limit=unlimited",
        "--filter=tags:*",
    ]

    get_digests_process = subprocess.run(
        gcloud_untagged_cmd, capture_output=True, text=True
    ).stdout
    digests_output = list(filter(lambda x: len(x) > 1, get_digests_process.split("/n")))

    if digests_output:
        images = list(map(lambda digest: f"{image_repo_path}@{digest}", digests_output))
        return images


def recursive_untagged_images_lookup(
    root_repository: str, wait_time: Optional[int] = None
) -> List[str]:
    """
    Given a base iamge, recurisvely searches for untagged images
    in all repositories/subdirectories.

    Returns a list with all those images
    """

    repositories_stack = []
    total_untagged_images = []

    repositories_stack.append(root_repository)

    while repositories_stack:
        current_repository = repositories_stack.pop()
        current_untagged_images = get_untagged_images(
            image_repo_path=current_repository
        )

        # child image repos/dirs that `may possibly` contain untagged versions.
        candidate_images = image_lookup(repository=current_repository)

        if current_untagged_images:
            total_untagged_images.extend(current_untagged_images)

        if candidate_images:
            repositories_stack.extend(candidate_images)

        if wait_time:
            time.sleep(wait_time)

    return total_untagged_images


def delete_images(images: List[str], chunksize: int = 20) -> None:
    """
    Deletes a sequence of images by chunks given their path:
    image_path@DIGEST
    """

    gcloud_del_cmd = (
        lambda img: f"gcloud container images delte {img} --quiet"
    )  # noqa: E731

    images_chunks = [
        images[i : i + chunksize]  # noqa: E203
        for i in range(0, len(images), chunksize)
    ]

    for chunk in images_chunks:
        images_str = " ".join(chunk)
        curr_del_cmd = gcloud_del_cmd(img=images_str)
        subprocess.run(curr_del_cmd)


def orchestrator(repositories: List[str]) -> None:
    """
    Given a list of repositories, searches for all dangling images
    and deletes them.
    """
    for repository in repositories:
        images = recursive_untagged_images_lookup(
            root_repository=repository, wait_time=1
        )

        if not images:
            continue
        delete_images(images=images)
