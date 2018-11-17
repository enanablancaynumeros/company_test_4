import contextlib
from os import path
from glob import glob

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory


alembic_cfg = Config()
scripts_folder = path.dirname((path.abspath(__file__)))
alembic_cfg.set_main_option("script_location", scripts_folder)
script = ScriptDirectory.from_config(alembic_cfg)


def alembic_table_exists():
    from connectors.db_connection import get_db_session_scope

    with get_db_session_scope() as session:
        return session.execute("SELECT to_regclass('alembic_version');").first()[0]


def get_current_revision_in_db():
    from connectors.db_connection import get_db_session_scope

    if not alembic_table_exists():
        return None
    with get_db_session_scope() as session:
        res = session.execute("""select version_num from alembic_version""")
        res = res.first()
        if res:
            return int(res[0])
        return res


def check_no_pending_migrations():
    class EmtpyException(Exception):
        pass

    class OkException(Exception):
        pass

    def raise_if_pending_migrations(migration_context, rev, generated_revisions):
        if generated_revisions[0].upgrade_ops.is_empty():
            raise OkException()
        else:
            raise EmtpyException(
                f'There are changes in the models not reflected in the alembic'
                f' scripts: {generated_revisions[0].upgrade_ops.as_diffs()}'
            )

    with contextlib.suppress(OkException):
        command.revision(
            alembic_cfg,
            autogenerate=True,
            process_revision_directives=raise_if_pending_migrations,
        )


def check_scripts_do_not_have_conflicts():
    if latest_revision_in_scripts() + 1 != len(get_all_script_files()):
        raise Exception(
            f'Conflicts found in the alembic migration scripts.'
            f'There are {script.get_current_head() + 1} revisions '
            f'ids and {len(get_all_script_files())} files.'
        )


def latest_revision_in_scripts():
    return int(script.get_current_head())


def alembic_upgrade_head():
    command.upgrade(alembic_cfg, revision="head")


def downgrade_version(revision):
    revision = format_revision(revision)
    command.downgrade(alembic_cfg, revision=revision)


def alembic_downgrade_base():
    downgrade_version(revision='base')


def generate_migration_script():
    rev_id = get_next_id()
    command.revision(
        alembic_cfg, autogenerate=True, rev_id=rev_id, message="Change this"
    )


def format_revision(rev_id):
    """
    Args:
        rev_id (Union[int, str]):

    Returns:
        str
    """
    if (
        isinstance(rev_id, int)
        or rev_id not in {'base', 'head'}
        and not rev_id.startswith('0')
    ):
        return f'0{rev_id}'
    return rev_id


def get_next_id():
    all_files = get_all_script_files()
    if all_files:
        rev_id = max(int(path.basename(x).split("_")[0]) for x in all_files)
        rev_id += 1
    else:
        rev_id = 0
    rev_id = format_revision(rev_id)
    return rev_id


def get_all_script_files():
    versions_folder = path.join(scripts_folder, "versions/*.py")
    return glob(versions_folder)
