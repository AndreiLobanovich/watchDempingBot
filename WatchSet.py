from utils import Origin, Watch


class WatchSet:
    watches: dict[Watch, list[Watch]] = {}
    postponed_other: list[Watch] = []

    def add_watch(self, watch: Watch):
        if watch.origin is Origin.HOME:
            if watch not in self.watches.keys():
                self.watches[watch] = []
                if self.postponed_other:
                    matching_watch_list = list(filter(lambda w: w.ref == watch.ref, self.postponed_other))
                    while matching_watch_list:
                        matching_watch = matching_watch_list.pop()
                        self.watches[watch].append(matching_watch)
                        self.postponed_other.remove(matching_watch)
        else:
            home_watch_list = list(filter(lambda w: w.ref == watch.ref, self.watches.keys()))
            if home_watch_list:
                home_watch = home_watch_list[0]
                self.watches[home_watch].append(watch)
            else:
                self.postponed_other.append(watch)

    def get_demping_cases(self) -> dict[Watch: list[Watch]]:
        demping_cases: dict[Watch: list[Watch]] = {}
        for home, other_list in self.watches.items():
            other_list_lower = list(filter(lambda w: w.price < home.price and w.is_set(), other_list))
            if other_list_lower:
                demping_cases.update({home: other_list_lower})
        return demping_cases
