import json
from argparse import Namespace

from caelestia.utils.scheme import (
    Scheme,
    get_scheme,
    get_scheme_flavours,
    get_scheme_modes,
    get_scheme_names,
    scheme_variants,
)
from caelestia.utils.theme import apply_colours


class Set:
    args: Namespace
    fallback_name = "caelestia"
    fallback_flavour = "default"

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def _pick_compatible_flavour(self, name: str, flavour: str, mode: str) -> str | None:
        flavours = get_scheme_flavours(name)

        if flavour in flavours and mode in get_scheme_modes(name, flavour):
            return flavour

        for candidate in flavours:
            if mode in get_scheme_modes(name, candidate):
                return candidate

        return None

    def _resolve_mode_target(
        self,
        name: str,
        flavour: str,
        mode: str,
        *,
        allow_fallback_scheme: bool,
    ) -> tuple[str, str] | None:
        compatible_flavour = self._pick_compatible_flavour(name, flavour, mode)
        if compatible_flavour is not None:
            return name, compatible_flavour

        if not allow_fallback_scheme:
            return None

        fallback_flavour = self._pick_compatible_flavour(self.fallback_name, self.fallback_flavour, mode)
        if fallback_flavour is None:
            return None

        return self.fallback_name, fallback_flavour

    def run(self) -> None:
        scheme = get_scheme()

        if self.args.notify:
            scheme.notify = True

        if self.args.random:
            scheme.set_random()
            apply_colours(scheme.colours, scheme.mode)
        elif self.args.name or self.args.flavour or self.args.mode or self.args.variant:
            target_name = self.args.name or scheme.name
            target_flavour = self.args.flavour or scheme.flavour

            if self.args.mode and not self.args.flavour:
                resolved_target = self._resolve_mode_target(
                    target_name,
                    target_flavour,
                    self.args.mode,
                    allow_fallback_scheme=not self.args.name,
                )
                if resolved_target is not None:
                    target_name, target_flavour = resolved_target

            if target_name != scheme.name:
                scheme.name = target_name
            if target_flavour != scheme.flavour:
                scheme.flavour = target_flavour
            if self.args.mode:
                scheme.mode = self.args.mode
            if self.args.variant:
                scheme.variant = self.args.variant
            apply_colours(scheme.colours, scheme.mode)
        else:
            print("No args given. Use --name, --flavour, --mode, --variant or --random to set a scheme")


class Get:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        scheme = get_scheme()

        if self.args.name or self.args.flavour or self.args.mode or self.args.variant:
            if self.args.name:
                print(scheme.name)
            if self.args.flavour:
                print(scheme.flavour)
            if self.args.mode:
                print(scheme.mode)
            if self.args.variant:
                print(scheme.variant)
        else:
            print(scheme)


class List:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        multiple = [self.args.names, self.args.flavours, self.args.modes, self.args.variants].count(True) > 1

        if self.args.names or self.args.flavours or self.args.modes or self.args.variants:
            if self.args.names:
                if multiple:
                    print("Names:", *get_scheme_names())
                else:
                    print("\n".join(get_scheme_names()))
            if self.args.flavours:
                if multiple:
                    print("Flavours:", *get_scheme_flavours())
                else:
                    print("\n".join(get_scheme_flavours()))
            if self.args.modes:
                if multiple:
                    print("Modes:", *get_scheme_modes())
                else:
                    print("\n".join(get_scheme_modes()))
            if self.args.variants:
                if multiple:
                    print("Variants:", *scheme_variants)
                else:
                    print("\n".join(scheme_variants))
        else:
            current_scheme = get_scheme()
            schemes = {}
            for scheme in get_scheme_names():
                schemes[scheme] = {}
                for flavour in get_scheme_flavours(scheme):
                    s = Scheme(
                        {
                            "name": scheme,
                            "flavour": flavour,
                            "mode": current_scheme.mode,
                            "variant": current_scheme.variant,
                            "colours": current_scheme.colours,
                        }
                    )
                    modes = get_scheme_modes(scheme, flavour)
                    if s.mode not in modes:
                        s._mode = modes[0]
                    try:
                        s._update_colours()
                        schemes[scheme][flavour] = s.colours
                    except ValueError:
                        pass

            print(json.dumps(schemes))
