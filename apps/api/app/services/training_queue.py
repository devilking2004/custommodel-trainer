from redis import Redis
from rq import Queue
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.training_job import TrainingJob
from app.workers.jobs import run_training_job


def enqueue_training_job(db: Session, training_job: TrainingJob) -> TrainingJob:
    settings = get_settings()
    redis_conn = Redis.from_url(settings.redis_url)
    queue = Queue(settings.rq_queue_name, connection=redis_conn)
    rq_job = queue.enqueue(run_training_job, training_job.id, job_timeout="30m")
    training_job.rq_job_id = rq_job.id
    db.add(training_job)
    db.commit()
    db.refresh(training_job)
    return training_job
