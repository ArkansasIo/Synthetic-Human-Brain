#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum JobKind { Simulation, Recording, Analysis, Export, Maintenance }

#[derive(Debug, Clone)]
pub struct Job { pub id: String, pub kind: JobKind, pub status: String }

#[derive(Debug, Default)]
pub struct JobQueue { jobs: Vec<Job> }

impl JobQueue {
    pub fn enqueue(&mut self, job: Job) { self.jobs.push(job); }
    pub fn pending(&self) -> &[Job] { &self.jobs }
}
