from aiohttp import ClientSession
from bs4 import BeautifulSoup


class AnitakuWrapper:
    def __init__(self):
        self.BASE_URL = "https://anitaku.to/"

        self.SEARCH_URL = f"{self.BASE_URL}/filter.html?keyword="

        self.FILTERS = {
            "ONGOING": "&status[]=Ongoing",
            "UPCOMING": "&status[]=Upcoming",
            "COMPLETED": "&status[]=Completed",
        }

        self._client = None

    async def __aenter__(self):
        self._client = ClientSession()
        return self

    async def __aexit__(self, *args):
        await self._client.close()

    async def search(self, anime_name: str, filters=None):
        """
        Searches the Anitaku website for the specified anime name and returns a list of anime names and urls.

        Parameters:
        anime_name (str): the name of the anime to search for.
        filters (list): a list of filters to apply to the search. Defaults to ongoing and upcoming anime.
                options: "ONGOING", "UPCOMING", "COMPLETED"

        Returns:
        list: Dictionaries containing the name, url, full_url, href, and image of the anime.
        """

        if filters is None:
            filters = ["ONGOING", "UPCOMING"]
        filtered_url = f"{self.SEARCH_URL}{anime_name}"

        for filter in filters:
            if filter in self.FILTERS:
                filtered_url += self.FILTERS[filter]

        async with self._client.get(filtered_url) as response:
            data = await response.text()

        soup = BeautifulSoup(data, "lxml")
        try:
            results = soup.find("ul", class_="items").find_all("li")
        except AttributeError:
            return []

        def find_name(element):
            return element.find("p", class_="name").text.strip()

        def find_href(element):
            return element.find("a")["href"]

        def find_image(element):
            return element.find("img")["src"]

        search_results = []
        for result in results:
            href = find_href(result)

            name = find_name(result)
            image = find_image(result)

            search_results.append(
                {
                    "name": name,
                    "url": href.split("/category/")[-1],
                    "full_url": f"{self.BASE_URL}{href}",
                    "href": href,
                    "image": image,
                }
            )

        return search_results

    async def get_status(self, anime_url):
        """
        Gets the status of the specified anime.

        Parameters:
        anime_url (str): the url of the anime to check for status.

        Returns:
        str: the status of the anime.
             Ongoing, Upcoming, or Completed
        """
        if not anime_url.startswith("/category/"):
            anime_url = f"/category/{anime_url}"

        async with self._client.get(f"{self.BASE_URL}{anime_url}") as response:
            data = await response.text()

        soup = BeautifulSoup(data, "lxml")
        try:
            status_div = soup.find("div", {"class": "anime_info_body_bg"}).find_all("p")[5]
        except AttributeError:
            return None

        return status_div.find("a").text

    async def has_episode_zero(self, anime_url):
        """
        Checks if the specified anime has episode zero.

        Parameters:
        anime_url (str): the url of the anime to check for episode zero.

        Returns:
        bool: True if the anime has episode zero, False otherwise.
        """
        async with self._client.get(f"{self.BASE_URL}{anime_url}") as response:
            data = await response.text()
        soup = BeautifulSoup(data, "lxml")
        error = soup.find("div", {"class": "anime_name new_series"}).text.strip()
        if error == "404 Not Found":
            return False
        return True

    async def get_new_episode(self, anime_url):
        """
        Gets the latest episode number of the specified anime.

        Parameters:
        anime_url (str): the url of the anime to retrieve the latest episode for.

        Returns:
        int: latest episode number
        """
        if not anime_url.startswith("/category/"):
            anime_url = f"/category/{anime_url}"

        async with self._client.get(f"{self.BASE_URL}{anime_url}") as response:
            data = await response.text()

        soup = BeautifulSoup(data, "lxml")
        try:
            ul_li = soup.find("ul", id="episode_page").find_all("li")
        except AttributeError:
            return None
        # The last element in the list has the latest episode within the attribute ep_end
        return int(ul_li[-1].find("a")["ep_end"])
