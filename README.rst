Python package boilerplate (IDU) 
================================

.. logo-start

.. figure:: https://sun9-46.userapi.com/impf/aUFBStH0x_6jN9UhgwrKN1WN4hZ9Y2HMMrXT2w/NuzVobaGlZ0.jpg?size=1590x400&quality=95&crop=0,0,1878,472&sign=9d33baa41a86de35d951d4bbd8011994&type=cover_group
   :alt: The Institute of Design and Urban Studies

.. logo-end

|Documentation Status| |PythonVersion| |Black|

.. readme-start 

Installation
------------

The library can be installed with ``pip``:

::

   pip install git+https://github.com/vasilstar97/python-package-boilerplate@main


How to use
----------

Use the library by importing classes from ``my_package``:

::

   from my_package.my_module_1 import MyClass

For more detailed use case see our `examples <#examples>`__.

Городской дашборд
-----------------

В репозитории есть воспроизводимый пайплайн для Высоцкого городского поселения:

-  ``notebooks/vysokoye_research.ipynb`` — расчёт квартальных показателей;
-  ``notebooks/dashboard.ipynb`` — сборка автономного HTML-дашборда;
-  ``my_package/service_catalog.py`` — группы, алиасы, комбинированные индексы
   и оценка ёмкости сервисов по площади участка или типу;
-  ``my_package/accessibility.py`` — объединение доступности по дорожной и пешеходной сетям;
-  ``my_package/statistics.py`` — статистика и фильтры по кварталам;
-  ``my_package/dashboard.py`` и ``my_package/dashboard_template.py`` — дашборд.

Запуск::

   jupyter nbconvert --to notebook --execute --inplace notebooks/vysokoye_research.ipynb
   jupyter nbconvert --to notebook --execute --inplace notebooks/dashboard.ipynb

Результат сохраняется в ``notebooks/data/vysokoye/dashboard.html``. Дашборд не
требует API-ключей; тайлы загружаются с OpenStreetMap/Esri, остальные данные
встроены в HTML.

Показатели
~~~~~~~~~~

-  **OSR** — открытость застройки, а не доля озеленения.
-  **green_share** — доля лесов, парков и озеленённых территорий landuse.
-  **area_accessibility** — среднее пешеходное время доступности квартала
   (5 км/ч) по дорожной или пешеходной сети: для каждой пары кварталов
   берётся лучший маршрут.
-  **green_access_m** — расстояние до публичной зелени по дорожной или
   пешеходной сети; в пределах 500 м строится флаг ``green_access_500``.
-  **provision_strong_*** — обеспеченность отдельными сервисами; для
   взаимозаменяемых услуг дополнительно считаются ``grocery``
   (супермаркеты + магазины у дома) и ``parks`` (парки + заповедники).
   Для каждого сервиса в ``results.geojson`` также сохраняются
   ``access_time_*``, ``service_demand_*``, ``service_served_*`` и
   ``service_capacity_*``; они показываются в подсказке квартала при выборе
   показателя обеспеченности.
-  **Статистика** — пересчитывается по произвольным фильтрам, показывает
   ``n``, пропуски и помечает группы с ``n < 5``.

Ограничения: население и ёмкость большинства сервисов импутируются, поэтому
показатели нельзя использовать как официальную статистику. Ёмкость полигонов
оценивается по ближайшему нормативному размеру участка BlocksNet, точечных
объектов — по минимальному нормативу типа; источник указан в
``capacity_source``.

Data
----

All the required data is stored in `examples
data folder <./examples/data>`__.

Examples
--------

Next examples will help one to get used to the library:

1. Main `example <./examples/my_example.ipynb>`__ of the library.
2. ...

Documentation
-------------

Detailed information and description of the library is available in
`documentation <https://vasilstar97.github.io/python-package-boilerplate/>`__.

Project Structure
-----------------

The latest version of the library is available in the ``main`` branch.

The repository includes the following directories and modules:

-  `my_package <./my_package>`__
   directory with the library code:

   -  ...
   -  ...

-  `tests <./tests>`__
   ``pytest`` testing
-  `examples <./examples>`__
   examples of how the library works
-  `docs <./docs>`__
   documentation sources

Developing
----------

...

License
-------

The project has `BSD-3-Clause license <./LICENSE>`__

Acknowledgments
---------------

...

Contacts
--------

You can contact me:

-  `Vasilii Starikov <https://t.me/vasilstar>`__ - assistant

Also, you are welcomed to the `issues <./issues>`__ section!

Publications
------------

-  `My publication name from scholar or something <https://scholar.google.com/>`__
-  ...

.. |Documentation Status| image:: https://github.com/vasilstar97/python-package-boilerplate/actions/workflows/documentation.yml/badge.svg?branch=main
   :target: https://vasilstar97.github.io/python-package-boilerplate/
.. |PythonVersion| image:: https://img.shields.io/badge/python-3.10-blue
   :target: https://pypi.org/project/geopandas/
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. readme-end
