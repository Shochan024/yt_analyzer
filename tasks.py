# tasks.py

from invoke import Collection, task

from src.yt_analyzer.application.performance_metrics_command import (
  run_performance_metrics,
)
from src.yt_analyzer.application.pipeline_command import run_all_pipeline
from src.yt_analyzer.application.statistics_command import (
  run_long_statistics,
  run_short_statistics,
)
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
  output_path = run_title_features(video_id=video_id)
  print(f"Written: {output_path}")


@task
def metrics(c, video_id=None):
  output_path = run_performance_metrics(video_id=video_id)
  print(f"Written: {output_path}")


@task(name="long")
def statistics_long(c):
  output_path = run_long_statistics()
  print(f"Written: {output_path}")


@task(name="short")
def statistics_short(c):
  output_path = run_short_statistics()
  print(f"Written: {output_path}")


@task(name="all")
def pipeline_all(c):
  run_all_pipeline()


title = Collection("title")
title.add_task(features)

performance = Collection("performance")
performance.add_task(metrics)

statistics = Collection("statistics")
statistics.add_task(statistics_long)
statistics.add_task(statistics_short)

pipeline = Collection("pipeline")
pipeline.add_task(pipeline_all)

ns = Collection()
ns.add_task(test)
ns.add_collection(title)
ns.add_collection(performance)
ns.add_collection(statistics)
ns.add_collection(pipeline)
