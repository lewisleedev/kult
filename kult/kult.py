"""
                                  
    _/    _/  _/    _/  _/    _/_/_/_/_/   
   _/  _/    _/    _/  _/        _/        
  _/_/      _/    _/  _/        _/         
 _/  _/    _/    _/  _/        _/          
_/    _/    _/_/    _/_/_/_/  _/           

Kyunghee University Library Toolkit v0.1.0a1
Created by Soonhyeok "Lewis" Lee

PERSONAL USE ONLY

"""

from base64 import b64encode
from urllib import parse
from datetime import datetime, timedelta
from xml.dom.minidom import parseString

import requests


class Client:
    """
    Main class to make requests to the library's server.

    Args:
            student_id (_type_): Student ID
            campus (str, optional): Student's Campus. Defaults to "S".
    """

    def __init__(self, student_id, campus="S") -> None:
        self.student_id = student_id
        self.campus = campus
        self.encoded_id = b64encode(str(student_id).encode())
        self.def_header = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.78 Mobile Safari/537.36",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _make_url(self, path: str, query: str = None) -> str:
        """
        Returns a URL to make requests to.

        Args:
            path (str): path to a URL.
            query (str, optional): Query to append to a url. Defaults to None.

        Returns:
            str: url
        """
        if query:
            return "ipaddr" + path + parse.urlencode(query)
        else:
            return "ipaddr" + path

    def get_user_data(self) -> dict:
        """
        Returns a dictionary of given user(student)'s data.

        Returns:
            dict: Dictonary of given user(student)'s data. If the user is currently using a seat, current seat data will also be returned.
        """

        def _get_value_from_xml(parsed, tagname: str) -> str:
            return parsed.getElementsByTagName(tagname)[0].firstChild.nodeValue

        result = {}

        query = {"real_id": self.encoded_id, "devide_gb": "A", "campus_gb": self.campus}

        seat_query = {
            "real_id": self.encoded_id,
            "version_gb": "N",
            "campus_gb": self.campus,
        }

        r = requests.post(
            self._make_url("mobile/MAN/xml_userInfo.php?", query),
            headers=self.def_header,
            timeout=5,
        )

        seat_r = requests.post(
            self._make_url("mobile/MAN/xml_mySeatStatus_list.php?", seat_query),
            headers=self.def_header,
            timeout=5,
        )

        parsed = parseString(r.content.decode("utf-8"))
        seat_parsed = parseString(seat_r.content.decode("utf-8"))

        result["status"] = _get_value_from_xml(parsed, "user_patName")
        result["department"] = _get_value_from_xml(parsed, "user_deptName")
        result["name"] = _get_value_from_xml(parsed, "user_name")

        dt_format = "%Y%m%d%H&M%S"  # start/endtime format ex) 20220817220307

        try:
            result["room_using"] = _get_value_from_xml(seat_parsed, "seat_room_name")
            result["room_no"] = _get_value_from_xml(seat_parsed, "seat_room_no")
            result["seat_using"] = _get_value_from_xml(seat_parsed, "seat_seat_no")

            start_time_str = _get_value_from_xml(seat_parsed, "seat_start_time")
            end_time_str = _get_value_from_xml(seat_parsed, "seat_end_time")

            result["seat_start_time"] = datetime.strptime(start_time_str, dt_format)
            result["seat_end_time"] = datetime.strptime(end_time_str, dt_format)

        except:
            result["room_using"] = ""
            result["seat_using"] = ""

        return result

    def get_seat_history(self, min_duration: int = 0) -> list:
        """
        Returns the list of dictionaries containing user's seat history.

        Args:
            min_duration (int, optional): Minimum duration of record to be returned. If you set this to 20, for example, the function will only return visit records with the difference between end time and start time higher than 20 minutes.
                                        This is useful because seat history retrieved from the original xml file does not have any indications that you have actually entered the library & used the seat. Defaults to 0.

        Returns:
            list: _description_
        """

        if min_duration < 0:
            raise ValueError("Minumum duration cannot be lower than 0.")
        elif min_duration > 1440:  # 24?????? ??????
            raise ValueError("Too big minimum duration.")

        query = {
            "real_id": self.encoded_id,
            "room_gb": 1,  # ?????? ?????? (????????????, ?????????????????? ??????)
            "campus_gb": self.campus,
        }

        r = requests.post(
            self._make_url("mobile/MAN/xml_My_Seat_History.php?", query),
            headers=self.def_header,
            timeout=5,
        )

        rslt = r.content.decode("utf-8")

        rslt = parseString(rslt)

        valuable = ["room_name", "seat_info"]

        history_arr = []

        for item in rslt.getElementsByTagName("item"):
            item_arr = {}
            for element in item.childNodes:
                if element.tagName in valuable:
                    item_arr[element.tagName] = element.firstChild.nodeValue

                elif element.tagName == "use_time":

                    rslt_usetime = element.firstChild.nodeValue

                    date = rslt_usetime.split()[0]
                    t_arr = rslt_usetime.split()[1].split("~")
                    start_time = date + " " + t_arr[0]
                    end_time = date + " " + t_arr[1]

                    start_pytime = datetime.strptime(start_time, "%Y.%m.%d %H:%M")
                    end_pytime = datetime.strptime(end_time, "%Y.%m.%d %H:%M")

                    if end_pytime < start_pytime:
                        end_pytime = end_pytime + timedelta(
                            days=1
                        )  # ??????????????? 24??? ????????? ?????? ?????? ?????????

                    item_arr["start_time"] = start_pytime
                    item_arr["end_time"] = end_pytime
                    item_arr["duration"] = end_pytime - start_pytime

                else:
                    pass

            if min_duration == 0:
                history_arr.append(item_arr)
            else:
                if item_arr["duration"] >= timedelta(minutes=min_duration):
                    history_arr.append(item_arr)
                else:
                    pass

        return history_arr

    def set_seat(self, seat_no: int, room_no: int) -> int:
        """
        Books a given seat in a given room.

        Args:
            seat_no (int): seat number
            room_no (int): room number

        Returns:
            int: Result code.
        """

        return_codes = {
            "?????? ????????? ?????? ????????? ??????????????????.": 201,
            "?????? ????????? ????????? ????????????.": 202,
            "01?????? ????????? ???????????? ????????? ?????? ?????????.": 203,
            "????????? ?????????????????????. \n 20????????? ????????? WIFI??? ??????????????? ?????? ???????????? ?????????": 100,
            "????????? ?????????????????????. \n 20????????? GATE??? ???????????? ??????????????? ?????? ???????????? ?????????..": 100,
        }

        query = {
            "real_id": self.encoded_id,
            "seat_no": seat_no,
            "room_no": room_no,
            "campus_gb": self.campus,
        }

        r = requests.post(
            self._make_url("mobile/MAN/setSeatGate.php?"),
            query,
            headers=self.def_header,
            timeout=5,
        )

        result_msg = (
            parseString(r.content.decode("utf-8"))
            .getElementsByTagName("result_msg")[0]
            .firstChild.nodeValue
        )

        return return_codes.get(result_msg, 200)

    def continue_seat(self, seat_no: int, room_no: int) -> int:
        """
        Continues using seat.

        Args:
            seat_no (int): Seat number
            room_no (int): Room Number

        Returns:
            int: return code
        """
        return_codes = {
            "????????? ?????????????????????.": 100,
            "????????? ???????????? 60???????????? ???????????????.": 201,  #
            "???????????? ?????? ????????? ?????????.1": 202,  # Unknown user
        }
        query = {
            "real_id": self.encoded_id,
            "seat_no": seat_no,
            "room_no": room_no,
            "campus_gb": self.campus,
        }

        r = requests.post(
            self._make_url("/mobile/MAN/xml_myseat_cont.php?", query),
            headers=self.def_header,
            timeout=5,
        )

        result_msg = (
            parseString(r.content.decode("utf-8"))
            .getElementsByTagName("result_msg")[0]
            .firstChild.nodeValue
        )

        result_code = return_codes.get(result_msg, 200)

        return result_code


# if __name__ == "__main__":
