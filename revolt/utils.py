__all__ = ("Missing",)

class _Missing:
    def __repr__(self):
        return "<Missing>"

Missing = _Missing()
