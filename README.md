# prey

Prey is project for scanning large networks and saving results into database.

### Basic Concept

Prey architecture is similiar with operating system. Core of application is
sheduler, which is responsible for sheduling a new tasks. Any scan engine is
only module, which is installed into sheduler. Like running application in
operating system.

This concept let's user to adjust which scanner should be used or create new
ones. Sheduling algorithms or task parallelism can be also adjusted very easily.

Scan engines are objects called supervisors. They are able to run new tasks and
provide information such as how many tasks are currently running, how many
tasks can be runned at once or how many tasks are waitinjg for run. Sheduler
comunicate with this supervisors, when deciding what should be started next.

Supervisors also provide list of unblockers.

### Task Parallelism

Tasks belonging a sing supervisour can be runned in parallel. Supervisor keeps
track of their count.

### Note

this project is under heavy development
