"""Seed the database with sample interaction data for testing."""

import asyncio
import random
from sqlmodel import select

from app.database import get_session
from app.models.item import ItemRecord
from app.models.interaction import InteractionLog
from app.models.learner import Learner


async def seed():
    """Create sample learners and interactions for all tasks."""
    async for session in get_session():
        # Get all tasks
        tasks = (await session.exec(select(ItemRecord).where(ItemRecord.type == "task"))).all()
        print(f"Found {len(tasks)} tasks")

        # Create learners
        learners = []
        for i in range(1, 51):
            learner = (await session.exec(select(Learner).where(Learner.external_id == f"student_{i}"))).first()
            if not learner:
                learner = Learner(external_id=f"student_{i}", student_group=f"group_{(i - 1) // 10 + 1}")
                session.add(learner)
                await session.flush()
            learners.append(learner)

        print(f"Have {len(learners)} learners")

        # Create interactions for each task
        count = 0
        for task in tasks:
            num_interactions = random.randint(20, 40)
            for _ in range(num_interactions):
                learner = random.choice(learners)
                score = random.gauss(70, 20)
                score = max(0, min(100, score))
                score = round(score, 1)

                interaction = InteractionLog(
                    learner_id=learner.id,
                    item_id=task.id,
                    kind="attempt",
                    score=score,
                    checks_passed=int(score // 10),
                    checks_total=10,
                )
                session.add(interaction)
                count += 1

        await session.commit()
        print(f"Created {count} interactions")
        return


if __name__ == "__main__":
    asyncio.run(seed())
