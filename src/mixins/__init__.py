from datetime import datetime
from datetime import timezone

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class MixinTimestamps():
  created_at: Mapped[datetime] = mapped_column(default = lambda: datetime.now(timezone.utc))
  updated_at: Mapped[datetime] = mapped_column(default = lambda: datetime.now(timezone.utc),
                                               onupdate = lambda: datetime.now(timezone.utc))

class MixinIncludesTags():
  # public
  def includes_tags(self, *args, ANY = False):
    tags_self = [t.tag for t in self.tags]
    return all(tag in tags_self for tag in args) if True != ANY else any(tag in tags_self for tag in args)
