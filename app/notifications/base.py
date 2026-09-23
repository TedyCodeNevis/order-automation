from abc import ABC,abstractmethod

class Notifier(ABC):

    @abstractmethod
    async def send(self,message:str) -> None:
        raise NotImplementedError