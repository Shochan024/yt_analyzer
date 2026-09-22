# tasks.py

from invoke import Collection, task

from src.yt_analyzer.application.title_features_command import run_title_features


@task
def test(c):
  c.run(
    "python -m unittest discover -s tests -p 'test_*.py'",
    env={"PYTHONPATH": "."},
    pty=True
  )


@task
def features(c, video_id=None):
  output_path = run_title_features(
    video_id=video_id
  )

  print(
    f"Written: {output_path}"
  )


title = Collection(
  "title"
)

title.add_task(
  features
)

ns = Collection()

ns.add_task(
  test
)

ns.add_collection(
  title
)
