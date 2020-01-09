# Projekt `yadata`


## Trieda Record

 * podtrieda dict
 * každý atribút je prípadne vybavený poznámkou (kvôli bounce)
 * poznámky sa vypisujú iba pri zápise na stdout, nie pri .save(ddir)
 * atribút triedy: dict mapujúci názvy metód na metódy

## Inštancia Record (spoločná funkčnosť)

 * gro funkcionality je implementované tu
 * `save(self,datadir)` ulož sa do tohto datadiru
 * `merge(self,other,methods):`
   * mergni do seba tento objekt "rovný" tebe
   * `methods` - slovník `key -> method_name` (?)
 * metódy: SET, POST, APPEND, DELETE
 * metódy vracajú mergeovateľný objekt bouncnutých polí

## Podtrieda Record

 * má "YAML tag"
 * vie rozpoznať `dict` ako svoj typ (`@classmethod`)
 * kód je v `__init.py__` datadiru.

## Inštancia podtriedy Record

 * vie vyrobiť `keyprefix`
 * implementuje `__eq__`
 * má subdir property (tá hrá rolu iba pri prvom uložení)

## Trieda Datadir

 * nechať subclass list zatiaľ
 * je tam ešte aj slovník ako to molo doteraz

## Inštancia Datadir

 * všetky záznamy musia byť zatypované
 * `__init__` importuje modul, v module sú podtriedy Record
 * má metódu `merge` - logika mergeovania je tu

