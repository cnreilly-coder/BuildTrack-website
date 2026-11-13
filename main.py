
from drafter import *
from dataclasses import dataclass


@dataclass
class Expense:
    """Store information about one project expense."""
    category: str
    description: str
    amount: float
    date: str


@dataclass
class Task:
    """Store information about one project task."""
    name: str
    due_date: str
    status: str
    completion: int


@dataclass
class Project:
    """Store the main information for a construction project."""
    name: str
    budget: float
    expenses: list[Expense]
    tasks: list[Task]
    manpower: int
    start_date: str
    deadline: str


@dataclass
class State:
    """Store information shared between BuildTrack pages."""
    projects: list[Project]
    selected_project_index: int
    message: str
    show_completed: bool


def total_expenses(project: Project) -> float:
    """Calculate the total amount spent on a project."""
    total = 0.0
    for expense in project.expenses:
        total += expense.amount
    return total


def average_task_completion(project: Project) -> float:
    """Calculate the average completion percentage of a project's tasks."""
    if len(project.tasks) == 0:
        return 0.0

    total = 0
    for task in project.tasks:
        total += task.completion

    return total / len(project.tasks)


def budget_percentage(project: Project) -> float:
    """Calculate the percentage of the project budget already spent."""
    return total_expenses(project) / project.budget * 100


@route
def index(state: State) -> Page:
    """Display the BuildTrack welcome page."""
    return Page(state, [
        "BUILDTRACK",
        "Construction Project Management",
        "",
        "Welcome to BuildTrack!",
        "Track budgets, expenses, manpower, and deadlines.",
        "",
        Button("View Dashboard", "dashboard_page"),
        Button("Add a Project", "add_project_page")
    ])


@route
def dashboard_page(state: State) -> Page:
    """Display project summaries on the dashboard."""
    content = [
        "BUILDTRACK DASHBOARD",
        "",
        state.message,
        ""
    ]

    if len(state.projects) == 0:
        content.append("You do not have any projects yet.")
    else:
        for index_number in range(len(state.projects)):
            project = state.projects[index_number]
            expenses = total_expenses(project)
            remaining = project.budget - expenses
            completion = average_task_completion(project)

            content.append("PROJECT: " + project.name)
            content.append("Original Budget: $" + str(project.budget))
            content.append("Total Expenses: $" + str(round(expenses, 2)))
            content.append("Remaining Budget: $" + str(round(remaining, 2)))
            content.append(
                "Task Completion: " + str(round(completion, 1)) + "%"
            )

            if expenses > project.budget:
                content.append("WARNING: Project is over budget!")
            elif len(project.tasks) > 0 and budget_percentage(project) > completion + 15:
                content.append("WARNING: Spending is ahead of project progress.")
            else:
                content.append("Project is currently within expected limits.")

            content.append(
                Button(
                    "View Project Details",
                    "project_details_page",
                    arguments={"project_index": index_number}
                )
            )
            content.append("")

    content.append(Button("Add a Project", "add_project_page"))
    content.append(Button("Home", "index"))
    return Page(state, content)


@route
def add_project_page(state: State) -> Page:
    """Display the form for creating a project."""
    return Page(state, [
        "ADD A PROJECT",
        "Enter the information for your new construction project.",
        "Project Name",
        TextBox("project_name"),
        "Project Budget",
        TextBox("budget", 0.0, kind="number"),
        "Number of Workers",
        TextBox("manpower", 0, kind="number"),
        "Start Date",
        TextBox("start_date"),
        "Project Deadline",
        TextBox("deadline"),
        Button("Create Project", "create_project"),
        Button("Back to Dashboard", "dashboard_page")
    ])


@route
def create_project(
    state: State,
    project_name: str,
    budget: float,
    manpower: int,
    start_date: str,
    deadline: str
) -> Page:
    """Create a project and add it to the project list."""
    if project_name.strip() == "":
        state.message = "Please enter a project name."
        return add_project_page(state)

    if budget <= 0:
        state.message = "The project budget must be greater than zero."
        return add_project_page(state)

    if manpower < 0:
        state.message = "The number of workers cannot be negative."
        return add_project_page(state)

    new_project = Project(
        project_name,
        budget,
        [],
        [],
        manpower,
        start_date,
        deadline
    )

    state.projects.append(new_project)
    state.selected_project_index = len(state.projects) - 1
    state.message = "Project created successfully!"
    return dashboard_page(state)


@route
def project_details_page(state: State, project_index: int) -> Page:
    """Display details for the selected project."""
    if project_index < 0 or project_index >= len(state.projects):
        state.message = "Project could not be found."
        return dashboard_page(state)

    state.selected_project_index = project_index
    state.show_completed = False
    project = state.projects[project_index]

    return Page(state, [
        "PROJECT DETAILS",
        "Project: " + project.name,
        "Budget: $" + str(project.budget),
        "Workers: " + str(project.manpower),
        "Start Date: " + project.start_date,
        "Deadline: " + project.deadline,
        "",
        Button(
            "Edit Project",
            "edit_project_page",
            arguments={"project_index": project_index}
        ),
        Button(
            "Budget and Expenses",
            "budget_page",
            arguments={"project_index": project_index}
        ),
        Button(
            "Schedule and Tasks",
            "schedule_page",
            arguments={"project_index": project_index}
        ),
        Button(
            "Risk Analysis",
            "risk_analysis_page",
            arguments={"project_index": project_index}
        ),
        Button("Back to Dashboard", "dashboard_page")
    ])


@route
def edit_project_page(state: State, project_index: int) -> Page:
    """Display the form for editing a project."""
    if project_index < 0 or project_index >= len(state.projects):
        state.message = "Project could not be found."
        return dashboard_page(state)

    state.selected_project_index = project_index
    project = state.projects[project_index]

    return Page(state, [
        "EDIT PROJECT",
        "Project Name",
        TextBox("project_name", project.name),
        "Project Budget",
        TextBox("budget", project.budget, kind="number"),
        "Number of Workers",
        TextBox("manpower", project.manpower, kind="number"),
        "Start Date",
        TextBox("start_date", project.start_date),
        "Project Deadline",
        TextBox("deadline", project.deadline),
        Button("Save Changes", "save_project_changes"),
        Button(
            "Cancel",
            "project_details_page",
            arguments={"project_index": project_index}
        )
    ])


@route
def save_project_changes(
    state: State,
    project_name: str,
    budget: float,
    manpower: int,
    start_date: str,
    deadline: str
) -> Page:
    """Save changes to the selected project."""
    if state.selected_project_index < 0:
        state.message = "No project is selected."
        return dashboard_page(state)

    if project_name.strip() == "":
        state.message = "Please enter a project name."
        return edit_project_page(state, state.selected_project_index)

    if budget <= 0:
        state.message = "The project budget must be greater than zero."
        return edit_project_page(state, state.selected_project_index)

    if manpower < 0:
        state.message = "The number of workers cannot be negative."
        return edit_project_page(state, state.selected_project_index)

    project = state.projects[state.selected_project_index]
    project.name = project_name
    project.budget = budget
    project.manpower = manpower
    project.start_date = start_date
    project.deadline = deadline

    state.message = "Project updated successfully!"
    return project_details_page(state, state.selected_project_index)


@route
def budget_page(state: State, project_index: int) -> Page:
    """Display the budget and expenses for a project."""
    if project_index < 0 or project_index >= len(state.projects):
        state.message = "Project could not be found."
        return dashboard_page(state)

    state.selected_project_index = project_index
    project = state.projects[project_index]

    expenses = total_expenses(project)
    remaining = project.budget - expenses

    content = [
        "BUDGET AND EXPENSES",
        "Project: " + project.name,
        "",
        "Original Budget: $" + str(project.budget),
        "Total Expenses: $" + str(expenses),
        "Remaining Budget: $" + str(remaining),
        ""
    ]

    if expenses > project.budget:
        content.append("WARNING: This project is over budget!")
    elif expenses == project.budget:
        content.append("WARNING: The entire project budget has been spent.")
    else:
        content.append("The project is currently within its budget.")

    content.append("")
    content.append("EXPENSE HISTORY")

    if len(project.expenses) == 0:
        content.append("No expenses have been added yet.")
    else:
        for expense in project.expenses:
            content.append("Category: " + expense.category)
            content.append("Description: " + expense.description)
            content.append("Amount: $" + str(expense.amount))
            content.append("Date: " + expense.date)
            content.append("")

    content.append(Button("Add an Expense", "add_expense_page"))
    content.append(
        Button(
            "Back to Project Details",
            "project_details_page",
            arguments={"project_index": project_index}
        )
    )
    return Page(state, content)


@route
def add_expense_page(state: State) -> Page:
    """Display the form for adding an expense."""
    if state.selected_project_index < 0:
        state.message = "Please select a project first."
        return dashboard_page(state)

    project = state.projects[state.selected_project_index]

    return Page(state, [
        "ADD AN EXPENSE",
        "Project: " + project.name,
        "",
        "Expense Category",
        TextBox("expense_category"),
        "Description",
        TextBox("expense_description"),
        "Amount",
        TextBox("expense_amount", 0.0, kind="number"),
        "Date",
        TextBox("expense_date"),
        "",
        Button("Save Expense", "create_expense"),
        Button(
            "Cancel",
            "budget_page",
            arguments={"project_index": state.selected_project_index}
        )
    ])


@route
def create_expense(
    state: State,
    expense_category: str,
    expense_description: str,
    expense_amount: float,
    expense_date: str
) -> Page:
    """Validate and save a new project expense."""
    if state.selected_project_index < 0:
        state.message = "Please select a project first."
        return dashboard_page(state)

    if expense_category.strip() == "":
        state.message = "Please enter an expense category."
        return add_expense_page(state)

    if expense_description.strip() == "":
        state.message = "Please enter an expense description."
        return add_expense_page(state)

    if expense_amount <= 0:
        state.message = "The expense amount must be greater than zero."
        return add_expense_page(state)

    project = state.projects[state.selected_project_index]

    new_expense = Expense(
        expense_category,
        expense_description,
        expense_amount,
        expense_date
    )

    project.expenses.append(new_expense)
    state.message = "Expense added successfully!"

    return budget_page(state, state.selected_project_index)


@route
def schedule_page(state: State, project_index: int) -> Page:
    """Display tasks and optionally filter to completed tasks."""
    if project_index < 0 or project_index >= len(state.projects):
        state.message = "Project could not be found."
        return dashboard_page(state)

    state.selected_project_index = project_index
    project = state.projects[project_index]

    completion = average_task_completion(project)
    completed_count = 0

    for task in project.tasks:
        if task.status == "Completed":
            completed_count += 1

    content = [
        "SCHEDULE AND TASKS",
        "Project: " + project.name,
        "Start Date: " + project.start_date,
        "Project Deadline: " + project.deadline,
        "",
        "Overall Task Completion: " + str(round(completion, 1)) + "%",
        "Completed Tasks: " + str(completed_count) +
        " out of " + str(len(project.tasks)),
        ""
    ]

    if state.show_completed:
        content.append("FILTER: SHOWING COMPLETED TASKS ONLY")
    else:
        content.append("FILTER: SHOWING ALL TASKS")

    content.append("")

    visible_tasks = 0

    if len(project.tasks) == 0:
        content.append("No tasks have been added yet.")
    else:
        for task_index in range(len(project.tasks)):
            task = project.tasks[task_index]

            if not state.show_completed or task.status == "Completed":
                visible_tasks += 1
                content.append("Task: " + task.name)
                content.append("Due Date: " + task.due_date)
                content.append("Status: " + task.status)
                content.append("Completion: " + str(task.completion) + "%")

                if task.status != "Completed":
                    content.append(
                        Button(
                            "Mark as Completed",
                            "mark_task_completed",
                            arguments={"task_index": task_index}
                        )
                    )
                else:
                    content.append("This task is finished!")

                content.append("")

        if visible_tasks == 0:
            content.append("There are no completed tasks to display.")

    if state.show_completed:
        content.append(
            Button("Show All Tasks", "toggle_task_filter")
        )
    else:
        content.append(
            Button("Show Completed Tasks", "toggle_task_filter")
        )

    content.append(Button("Add a Task", "add_task_page"))
    content.append(
        Button(
            "Back to Project Details",
            "project_details_page",
            arguments={"project_index": project_index}
        )
    )

    return Page(state, content)


@route
def toggle_task_filter(state: State) -> Page:
    """Switch between showing all tasks and completed tasks only."""
    if state.selected_project_index < 0:
        state.message = "Please select a project first."
        return dashboard_page(state)

    state.show_completed = not state.show_completed
    return schedule_page(state, state.selected_project_index)


@route
def add_task_page(state: State) -> Page:
    """Display the form for adding a task."""
    if state.selected_project_index < 0:
        state.message = "Please select a project first."
        return dashboard_page(state)

    project = state.projects[state.selected_project_index]

    return Page(state, [
        "ADD A TASK",
        "Project: " + project.name,
        "",
        "Task Name",
        TextBox("task_name"),
        "Due Date",
        TextBox("task_due_date"),
        "",
        Button("Save Task", "create_task"),
        Button(
            "Cancel",
            "schedule_page",
            arguments={"project_index": state.selected_project_index}
        )
    ])


@route
def create_task(
    state: State,
    task_name: str,
    task_due_date: str
) -> Page:
    """Validate and add a new task to the selected project."""
    if state.selected_project_index < 0:
        state.message = "Please select a project first."
        return dashboard_page(state)

    if task_name.strip() == "":
        state.message = "Please enter a task name."
        return add_task_page(state)

    if task_due_date.strip() == "":
        state.message = "Please enter a due date."
        return add_task_page(state)

    project = state.projects[state.selected_project_index]

    new_task = Task(
        task_name,
        task_due_date,
        "Not Started",
        0
    )

    project.tasks.append(new_task)
    state.message = "Task added successfully!"
    state.show_completed = False

    return schedule_page(state, state.selected_project_index)


@route
def mark_task_completed(state: State, task_index: int) -> Page:
    """Mark a selected task as completed."""
    if state.selected_project_index < 0:
        state.message = "Please select a project first."
        return dashboard_page(state)

    project = state.projects[state.selected_project_index]

    if task_index < 0 or task_index >= len(project.tasks):
        state.message = "Task could not be found."
        return schedule_page(state, state.selected_project_index)

    project.tasks[task_index].status = "Completed"
    project.tasks[task_index].completion = 100
    state.message = "Task marked as completed!"
    state.show_completed = False

    return schedule_page(state, state.selected_project_index)


@route
def risk_analysis_page(state: State, project_index: int) -> Page:
    """Compare project spending with task completion to identify risks."""
    if project_index < 0 or project_index >= len(state.projects):
        state.message = "Project could not be found."
        return dashboard_page(state)

    state.selected_project_index = project_index
    project = state.projects[project_index]

    expenses = total_expenses(project)
    spent_percentage = budget_percentage(project)
    completion = average_task_completion(project)

    content = [
        "PROJECT RISK ANALYSIS",
        "Project: " + project.name,
        "",
        "Original Budget: $" + str(project.budget),
        "Total Expenses: $" + str(expenses),
        "Budget Spent: " + str(round(spent_percentage, 1)) + "%",
        "Task Completion: " + str(round(completion, 1)) + "%",
        ""
    ]

    if expenses > project.budget:
        content.append("HIGH RISK: Project expenses exceed the original budget.")
    elif len(project.tasks) == 0:
        content.append("MORE DATA NEEDED: Add tasks to measure project progress.")
    elif completion == 0 and expenses > 0:
        content.append(
            "HIGH RISK: Money has been spent, but no tasks show completed progress."
        )
    elif spent_percentage > completion + 15:
        content.append(
            "WARNING: Spending is significantly ahead of project completion."
        )
    else:
        content.append("LOW RISK: Spending is reasonably aligned with task progress.")

    content.append("")
    content.append("PROJECTED FINAL COST")

    if completion > 0:
        projected_cost = expenses / (completion / 100)
        content.append(
            "Estimated Final Cost: $" + str(round(projected_cost, 2))
        )

        if projected_cost > project.budget:
            content.append(
                "WARNING: Current spending suggests a possible budget overrun."
            )
            content.append(
                "Estimated amount over budget: $" +
                str(round(projected_cost - project.budget, 2))
            )
        else:
            content.append("Current projection is within the original budget.")
    else:
        content.append("Not enough completed work to estimate final project cost.")

    content.append("")
    content.append(
        "Note: This projection assumes future spending continues at the "
        "same rate as completed work. It is an estimate, not a guarantee."
    )
    content.append(
        Button(
            "Back to Project Details",
            "project_details_page",
            arguments={"project_index": project_index}
        )
    )

    return Page(state, content)


start_server(State([], -1, "Welcome to BuildTrack!", False))

