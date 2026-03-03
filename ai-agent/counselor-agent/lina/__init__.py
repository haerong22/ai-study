from . import agent


"""
* `__init__.py`
    * 이 파일이 있는 폴더는 파이썬 패키지가 됩니다.
    * 이 파일은 해당 패키지의 '진입점(Entry Point)' 역할을 합니다.

* `from . import agent`
    * 패키지(폴더) 내의 `agent.py` 모듈을 외부로 노출(Export)시킵니다.

* Google ADK의 동작 방식
    1.  ADK는 `root_agent` 변수가 있는 모듈(파일)을 찾으려 합니다.
    2.  `__init__.py`가 `root_agent` 변수가 있는 `agent.py`을 노출시켜주기 때문에 ADK가 찾을 수 있습니다.
    3.  ADK는 `agent.py` 모듈 내의 `root_agent`라는 변수를 찾아 해당 패키지의 에이전트의 시작점으로 사용합니다.
"""