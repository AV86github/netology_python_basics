import os


class CookBook():
    """Class for Cooking book

    interface:
        get_book_as_dict
        get_shop_list_by_dishes
    """

    def __init__(self, file_path):
        self._file_path = file_path
        self._dict_book = {}
        self._dishes = set()

    def _read_book(self):
        """
        Read books and parse it to dict
        """
        if not os.path.isfile(self._file_path):
            return
        with open(self._file_path) as f:
            content = f.read()
        self._dict_book = self._pars_rec_arrays(content.split("\n\n"))

    def _pars_rec_arrays(self, rec_array):
        """
            array of rec to dict
        """
        result = {}
        for cur_rec in rec_array:
            # remoove empty string
            lines = [x for x in cur_rec.split("\n") if x]
            if len(lines) < 2:
                continue
            result.setdefault(lines[0], [])
            self._dishes.add(lines[0])
            if not self._check_ing_count(int(lines[1]), lines[2:]):
                print(f"Wrong ing count for {lines[0]}")
                continue
            for ing in lines[2:]:
                ing_items = [x.strip() for x in ing.split("|")]
                result[lines[0]].append({"ingredient_name": ing_items[0],
                                         "quantity": ing_items[1],
                                         "measure": ing_items[2]})
        return result

    def _check_ing_count(self, count, ings):
        return len(ings) == count

    def get_book_as_dict(self):
        """
        Getter
        return book as dict
        """
        if not self._dict_book:
            self._read_book()
        return self._dict_book

    def _get_dish_ing_for_person(self, dish, person_count):
        """return dict with ing:
        
        [description]
        
        Arguments:
            dish {[type]} -- [description]
            person_count {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        result = {}
        for ing in self._dict_book[dish]:
            result.setdefault(ing["ingredient_name"], {"quantity": int(ing["quantity"]) * person_count,
                                                       "measure": ing["measure"]})
        return result

    def _agragate_result(self, agregator, elem):
        """funsction summirize two dict.
        for existing element add quantity property
        
        [description]
        
        Arguments:
            agregator {[type]} -- [description]
            elem {[type]} -- [description]
        """
        for ing_name, ing_data in elem.items():
            if ing_name not in agregator.keys():
                agregator.setdefault(ing_name, ing_data)
            else:
                agregator[ing_name]["quantity"] += ing_data["quantity"]
        return agregator

    def get_shop_list_by_dishes(self, dishes, person_count):
        """return array of ingridients for person_count

        [description]
        """
        result = {}
        for dish in dishes:
            if dish not in self._dishes:
                continue

            result = self._agragate_result(result,
                    self._get_dish_ing_for_person(dish, person_count))
        return result


def main():
    cook_book = CookBook("recs.txt")
    cook_book.get_book_as_dict()
    print(cook_book.get_shop_list_by_dishes(['Омлет', 'Фахитос'], 3))


if __name__ == "__main__":
    main()
