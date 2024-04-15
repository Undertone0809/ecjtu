import re
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from ecjtu.constants import GET_CLASSES_URL, GET_GPA_URL
from ecjtu.models import GPA, ScheduledCourse, Score
from ecjtu.utils import get_cur_week_datetime, get_last_semester, get_today_date
from ecjtu.utils.logger import logger


class CRUDClient:
    """
    CRUD mixin for resources. This class provides basic CRUD operations for resources.
    """

    def __init__(self, client: requests.Session):
        self.client: requests.Session = client
        self.cache: dict = {}

    @abstractmethod
    def today(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def filter(self, *args, **kwargs):
        raise NotImplementedError


class ScheduledCourseCRUD(CRUDClient):
    def _fetch_courses(self, date: str) -> List[ScheduledCourse]:
        """Fetch courses by date

        Args:
            date(str): The date to fetch, eg: 2023-01-01

        Returns:
            List[ScheduledCourse]: List of courses
        """
        classes: List[ScheduledCourse] = []

        resp = self.client.post(GET_CLASSES_URL, data={"date": date})
        for k, v in resp.json().items():
            if k == "weekcalendarpojoList":
                for item in v:
                    cls = ScheduledCourse.model_validate(item)
                    logger.info(cls)
                    classes.append(cls)

        return classes

    def filter(self, *, date: str) -> List[ScheduledCourse]:
        """Filter courses by date

        Args:
            date(str): The date to filter, eg: 2023-01-01

        Returns:
            List[ElectiveCourse]: List of courses
        """
        return self._fetch_courses(date)

    def today(self) -> List[ScheduledCourse]:
        """Get today's classes

        Returns:
            List[ElectiveCourse]: List of courses
        """
        date: str = get_today_date()
        return self._fetch_courses(date)

    def this_week(self) -> List[List[ScheduledCourse]]:
        """Get this week's classes

        Returns:
            List[List[ElectiveCourse]]: List of courses
        """
        start_datetime: datetime = get_cur_week_datetime()
        week_classes: List[List[ScheduledCourse]] = []

        for i in range(7):
            date: str = (start_datetime + timedelta(days=i)).strftime("%Y-%m-%d")
            week_classes.append(self._fetch_courses(date))

        return week_classes


class GPACRUD(CRUDClient):
    def today(self) -> GPA:
        """Get current GPA

        Returns:
            GPA: GPA model
        """
        resp_html = self.client.get(GET_GPA_URL)

        if resp_html.status_code != 200:
            raise Exception(f"Failed to get GPA, status code: {resp_html.status_code}")

        soup = BeautifulSoup(resp_html.text, "html.parser")
        data = [td.text for td in soup.find_all("tr")[3].find_all("td")]
        return GPA.model_validate(
            {"student_name": data[1], "gpa": data[6], "status": data[2]}
        )

    def filter(self, **kwargs) -> List[GPA]:
        raise Exception("GAP can't be filtered")


class ScoreCRUD(CRUDClient):
    def _fetch_scores(self, semester: str) -> List[Score]:
        """Fetch scores by semester

        Args:
            semester(str): The semester to fetch, eg: 2023.1

        Returns:
            List[Score]: List of scores
        """
        resp_html = self.client.get(GET_GPA_URL)

        if resp_html.status_code != 200:
            raise Exception(f"Failed to get GPA, status code: {resp_html.status_code}")

        scores: List[Score] = []
        soup = BeautifulSoup(resp_html.text, "html.parser")

        pattern = re.compile(r"\b{}\b".format(semester.replace(".", "_")))
        ul_tags = soup.find_all("ul", class_=pattern)
        for ul_tag in ul_tags:
            li_list = ul_tag.find_all("li")
            li_values = [li.text for li in li_list]

            score = Score(
                semester=semester,
                course_name=li_values[1],
                course_nature=li_values[2],
                credit=float(li_values[4]),
                grade=li_values[5],
            )
            scores.append(score)

        return scores

    def today(self) -> List[Score]:
        """Get last semester's scores.

        The scores of this semester are not available until the semester ends.

        Returns:
            List[Score]: List of scores
        """
        semester = get_last_semester()
        return self._fetch_scores(semester)

    def filter(self, *, semester: Optional[str] = None, **kwargs) -> List[Score]:
        """Filter scores by specified conditions.

        Args:
            semester(Optional[str]): The semester to filter, eg: 2023.1, 2023.2

        Returns:
            List[Score]: List of scores
        """
        return self._fetch_scores(semester)
