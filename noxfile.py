import nox


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
def tests(session):
    session.install(".[testing]")
    session.run("pytest", "-svv")
