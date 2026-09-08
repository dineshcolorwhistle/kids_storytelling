"""
Seed Data for Curated Children's Stories
"""
from app.database.models import Story
from app.database.repositories.story_repository import StoryRepository
from app.utils.logger import logger

DEFAULT_STORIES = [
    {
        "title": "The Little Rabbit's Adventure",
        "description": "Barnaby the rabbit discovers a sparkling brook and dances with a butterfly.",
        "content": (
            "Once upon a time, in a bright green valley, lived a cheerful little rabbit named Barnaby. "
            "Barnaby loved to hop through the meadow and look for sweet wild clover. "
            "One sunny morning, he noticed a tiny blue butterfly resting on a golden dandelion. "
            "Good morning, little flutterby, Barnaby giggled. "
            "Together, they danced all the way to the whispering brook, where the water sparkled like diamonds. "
            "It was the happiest day in the whole forest."
        ),
        "estimated_duration": 30,
        "thumbnail_path": "rabbit.png"
    },
    {
        "title": "The Brave Little Lion",
        "description": "Leo the lion cub learns that helping a small bird is the truest kind of bravery.",
        "content": (
            "Under the warm golden sun of the savanna, a fluffy lion cub named Leo was practicing his roar. "
            "Instead of a mighty sound, only a soft squeak came out! Leo frowned and sat under an acacia tree. "
            "Just then, a baby robin called from a low branch, frightened by a curious beetle. "
            "Leo gently nudged the beetle away and smiled warmly at the little bird. "
            "True bravery is not about being loud, his mother whispered softly. It is about having a kind and helpful heart."
        ),
        "estimated_duration": 35,
        "thumbnail_path": "lion.png"
    },
    {
        "title": "The Gentle Elephant",
        "description": "Ellie the little elephant uses her big ears to listen to the whispering wind.",
        "content": (
            "Deep in the green jungle lived Ellie, a playful baby elephant with very big ears. "
            "Sometimes, Ellie wondered why her ears were so wide. "
            "One quiet afternoon, she spread her ears and listened closely. "
            "She could hear the gentle rustle of leaves, the secret hum of bees, and the laughter of monkeys far away. "
            "Your ears can hear the songs of the world, said her grandmother. "
            "Ellie swung her trunk with joy, proud of the music all around her."
        ),
        "estimated_duration": 35,
        "thumbnail_path": "elephant.png"
    },
    {
        "title": "The Lost Kitten Who Found a Home",
        "description": "Pip the tiny kitten searches for a cozy nap and finds a warm bowl of milk.",
        "content": (
            "A tiny calico kitten named Pip wandered into a sunny garden with green bushes and tall sunflowers. "
            "Pip gave a small meow and curled into a ball under a red wheelbarrow. "
            "Suddenly, a little girl opened the back door and saw two bright green eyes peeking out. "
            "Hello, sweet kitty, the girl said with a gentle smile. "
            "She brought out a warm saucer of milk and a soft blue blanket. Pip purred like a tiny motor, knowing he was home."
        ),
        "estimated_duration": 35,
        "thumbnail_path": "kitten.png"
    },
    {
        "title": "The Friendly Starlight",
        "description": "A sparkling star twinkles down to keep watch over sleepy forest dreamers.",
        "content": (
            "As dusk settled over the quiet hills, a tiny golden star named Stella woke up in the velvet sky. "
            "She peeked down through the fluffy clouds at all the sleepy creatures below. "
            "The ducklings were tucked under their mother's wings, and the deer rested beneath the oak trees. "
            "Stella twinkled as brightly as she could, casting a soft nightlight across the sleepy land. "
            "Sleep tight, little friends, Stella beamed, and the whole world drifted into sweet dreams."
        ),
        "estimated_duration": 30,
        "thumbnail_path": "star.png"
    },
    {
        "title": "Good Night, Forest Friends",
        "description": "A calming bedtime story as the woodland animals settle down for the night.",
        "content": (
            "The silver moon rose high above the tall pine trees, painting the forest in soft blue shadows. "
            "The busy squirrels climbed into their cozy nests, and the wise old owl gave a sleepy hoot from the hollow branch. "
            "The cool night breeze whispered a gentle lullaby through the leaves. "
            "Close your eyes, whispered the forest, as the crickets sang their peaceful midnight melody. "
            "Tomorrow will bring new adventures, but tonight is for calm, restful rest. Good night, little one."
        ),
        "estimated_duration": 40,
        "thumbnail_path": "moon.png"
    }
]

def seed_stories():
    """Populate database with default stories if empty."""
    current_count = StoryRepository.count()
    if current_count == 0:
        logger.info("Seeding initial children's stories...")
        for data in DEFAULT_STORIES:
            story = Story(
                id=None,
                title=data["title"],
                description=data["description"],
                content=data["content"],
                thumbnail_path=data["thumbnail_path"],
                estimated_duration=data["estimated_duration"]
            )
            StoryRepository.create(story)
        logger.info(f"Seeded {len(DEFAULT_STORIES)} default stories.")
    else:
        logger.info(f"Database already contains {current_count} stories. Skipping seed.")
