class User:
    def __init__(self, id: int, username: str, wins: int = 0):
        self.id = id
        self.username = username
        self.wins = wins

    def to_dict(self):
        return{
            "id": self.id,
            "username": self.username,
            "wins": self.wins
        }
    
    @staticmethod
    def from_dict(data):
        return User(data["id"], data["username"], data.get("wins", 0))
    
def get_list(users:dict[int, User]):
    return list(users.values())

def sort_list(users_list: list[User]):
    users_list[:] = sorted([user for user in users_list if user.wins > 0], key=lambda user: user.wins, reverse=True)
    