from __future__ import annotations

from collections.abc import MutableMapping, MutableSequence
import os.path as op

import wx

from amulet_map_editor.amulet_wx import simple

import amulet_nbt as nbt


class NBTEditor(simple.SimplePanel):

    image_list = None
    image_map = None

    def __init__(self, parent, nbt_data, root_tag_name="", callback=None):
        super(NBTEditor, self).__init__(parent)

        self.nbt_data = nbt_data

        if self.__class__.image_map is None and self.__class__.image_list is None:
            self.__class__.image_list = wx.ImageList(16, 16)
            self.__class__.image_map = {
                nbt.TAG_Byte: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_byte.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_Short: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_short.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_Int: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_int.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_Long: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_long.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_Float: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_float.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_Double: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_double.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_String: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_string.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_Compound: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_compound.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.NBTFile: self.image_list.ImageCount - 1,
                nbt.TAG_List: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_list.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_Byte_Array: self.image_list.Add(
                    wx.Image(
                        op.join("img", "nbt_tag_array.png"), wx.BITMAP_TYPE_PNG
                    ).ConvertToBitmap()
                ),
                nbt.TAG_Int_Array: self.image_list.ImageCount - 1,
                nbt.TAG_Long_Array: self.image_list.ImageCount - 1,
            }
        self.other = self.image_map[nbt.TAG_String]

        self.tree = self.build_tree(root_tag_name)
        self.add_object(self.tree, 0, wx.ALL | wx.CENTER | wx.EXPAND)

        nbt_button_row = simple.SimplePanel(self, wx.HORIZONTAL)
        self.add_tag_button = wx.Button(nbt_button_row, label="Add Tag")
        self.edit_tag_button = wx.Button(nbt_button_row, label="Edit Tag")
        nbt_button_row.add_object(self.add_tag_button)
        nbt_button_row.add_object(self.edit_tag_button)

        self.add_tag_button.Bind(wx.EVT_BUTTON, self.add_tag)
        self.edit_tag_button.Bind(wx.EVT_BUTTON, self.edit_tag)

        self.add_object(nbt_button_row, space=0)

        button_row = simple.SimplePanel(self, wx.HORIZONTAL)
        self.commit_button = wx.Button(button_row, label="Commit")
        self.cancel_button = wx.Button(button_row, label="Cancel")

        button_row.add_object(self.commit_button, space=0)
        button_row.add_object(self.cancel_button, space=0)

        self.commit_button.Bind(wx.EVT_BUTTON, self.commit)
        self.cancel_button.Bind(wx.EVT_BUTTON, self._close)

        self.add_object(button_row, space=0)

        self.callback = callback

    def commit(self, evt):
        self.callback(self.nbt_data)
        evt.Skip()

    def _close(self, evt):
        self.Close(True)
        evt.Skip()

    def build_tree(self, root_tag_name=""):
        def add_tree_node(_tree: wx.TreeCtrl, _parent, _items):
            for key, value in _items.items():
                new_child = None
                if isinstance(value, MutableMapping):
                    new_child = _tree.AppendItem(_parent, key)
                    add_tree_node(_tree, new_child, value)
                elif isinstance(value, MutableSequence):
                    new_child = _tree.AppendItem(_parent, key)

                    for item in value:
                        child_child = _tree.AppendItem(new_child, f"{item.value}")
                        tree.SetItemData(child_child, ("", item))
                        tree.SetItemImage(
                            child_child,
                            self.image_map.get(item.__class__, self.other),
                            wx.TreeItemIcon_Normal,
                        )
                else:
                    new_child = _tree.AppendItem(_parent, f"{key}: {value.value}")

                tree.SetItemData(new_child, (key, value))
                tree.SetItemImage(
                    new_child, self.image_map.get(value.__class__, self.other)
                )

        tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.EXPAND | wx.ALL)
        tree.AssignImageList(self.image_list)

        root = tree.AddRoot(root_tag_name)
        tree.SetItemData(root, (root_tag_name, self.nbt_data))
        tree.SetItemImage(
            root,
            self.image_map.get(
                self.nbt_data.__class__, self.image_map[nbt.TAG_Compound]
            ),
            wx.TreeItemIcon_Normal,
        )

        add_tree_node(tree, root, self.nbt_data)

        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.selection_changed)

        return tree

    def add_tag(self, evt):
        selected_tag = self.tree.GetFocusedItem()
        name, data = self.tree.GetItemData(selected_tag)

        def save_func(new_name, new_tag_value, new_tag_type, _):
            tag_type = [
                tag_class
                for tag_class in self.image_map
                if tag_class.__name__ == new_tag_type
            ][0]
            self.nbt_data[new_name] = nbt_tag = tag_type(new_tag_value)

            new_child = self.tree.AppendItem(
                selected_tag, f"{new_name}: {new_tag_value}"
            )
            self.tree.SetItemImage(new_child, self.image_map.get(tag_type, self.other))
            self.tree.SetItemData(new_child, (new_name, nbt_tag))

            print(self.nbt_data)

        add_dialog = EditTagDialog(
            self,
            "",
            nbt.TAG_Byte(0),
            [
                tag_type.__name__
                for tag_type in self.image_map.keys()
                if "TAG_" in tag_type.__name__
            ],
            create=True,
            save_callback=save_func,
        )
        add_dialog.Show()

    def edit_tag(self, evt):
        selected_tag = self.tree.GetFocusedItem()
        name, data = self.tree.GetItemData(selected_tag)
        print(name, data)

        def save_func(new_name, new_tag_value, new_tag_type, old_name):
            tag_type = [
                tag_class
                for tag_class in self.image_map
                if tag_class.__name__ == new_tag_type
            ][0]

            self.nbt_data[new_name] = nbt_tag = tag_type(new_tag_value)
            self.tree.SetItemImage(
                selected_tag, self.image_map.get(tag_type, self.other)
            )
            self.tree.SetItemData(selected_tag, (new_name, nbt_tag))

            if new_name != old_name:
                del self.nbt_data[old_name]

            print(self.nbt_data)

        edit_dialog = EditTagDialog(
            self,
            name,
            data,
            [
                tag_type.__name__
                for tag_type in self.image_map.keys()
                if "TAG_" in tag_type.__name__
            ],
            save_callback=save_func,
        )
        edit_dialog.Show()

    def selection_changed(self, evt):
        item = evt.GetItem()
        name, data = self.tree.GetItemData(item)

        if isinstance(data, MutableMapping):
            self.add_tag_button.Enable()
        elif isinstance(data, MutableSequence):
            self.add_tag_button.Enable()
        else:
            self.add_tag_button.Disable()


class EditTagDialog(wx.Frame):
    def __init__(
        self, parent, tag_name, tag, tag_types, create=False, save_callback=None
    ):
        super(EditTagDialog, self).__init__(
            parent, title="Edit NBT Tag", size=(500, 280)
        )

        self.save_callback = save_callback
        self.old_name = tag_name
        self.data_type_func = lambda x: x

        main_panel = simple.SimplePanel(self)

        name_panel = simple.SimplePanel(main_panel, sizer_dir=wx.HORIZONTAL)
        value_panel = simple.SimplePanel(main_panel, sizer_dir=wx.HORIZONTAL)
        tag_type_panel = simple.SimplePanel(main_panel)
        button_panel = simple.SimplePanel(main_panel, sizer_dir=wx.HORIZONTAL)

        name_label = simple.SimpleText(name_panel, "Name: ")
        self.name_field = wx.TextCtrl(name_panel)

        if tag_name == "" and not create:
            self.name_field.Disable()
        else:
            self.name_field.SetValue(tag_name)

        name_panel.add_object(name_label, space=0)
        name_panel.add_object(self.name_field, space=0)

        value_label = simple.SimpleText(value_panel, "Value: ")
        self.value_field = wx.TextCtrl(value_panel)

        if isinstance(tag, (nbt.TAG_Compound, nbt.TAG_List)):
            self.value_field.Disable()
        else:
            self.value_field.SetValue(str(tag.value))

        value_panel.add_object(value_label, space=0)
        value_panel.add_object(self.value_field, space=0)

        self.tag_type_group = wx.RadioBox(
            tag_type_panel, choices=tag_types, majorDimension=4
        )
        self.tag_type_group.SetSelection(
            self.tag_type_group.FindString(tag.__class__.__name__)
        )

        tag_type_panel.add_object(self.tag_type_group, space=0)

        self.save_button = wx.Button(button_panel, label="Save")
        self.cancel_button = wx.Button(button_panel, label="Cancel")

        button_panel.add_object(self.save_button, space=0)
        button_panel.add_object(self.cancel_button, space=0)

        main_panel.add_object(name_panel, space=0)
        main_panel.add_object(value_panel, space=0)
        main_panel.add_object(tag_type_panel, space=0)
        main_panel.add_object(button_panel, space=0)

        self.change_tag_type_func(self.tag_type_group.GetSelection())

        self.save_button.Bind(wx.EVT_BUTTON, self.save)
        self.cancel_button.Bind(wx.EVT_BUTTON, lambda evt: self.Close())

        self.value_field.Bind(wx.EVT_TEXT, self.value_changed)
        self.tag_type_group.Bind(wx.EVT_RADIOBOX, self.tag_type_change)

    def value_changed(self, evt):
        tag_value = evt.GetString()
        self.value_field.ChangeValue(str(self.data_type_func(tag_value)))

    def tag_type_change(self, evt):
        tag_type = evt.GetString()
        self.change_tag_type_func(tag_type)

    def change_tag_type_func(self, tag_type):
        self.data_type_func = lambda x: x
        if tag_type in ("TAG_Int", "TAG_Long", "TAG_Short", "TAG_Short", "TAG_Byte"):
            self.data_type_func = lambda x: int(float(x))
        elif tag_type in ("TAG_Float", "TAG_Double"):
            self.data_type_func = float

        if tag_type not in ("TAG_Byte_Array", "TAG_Int_Array", "TAG_Long_Array"):
            self.value_field.ChangeValue(
                str(self.data_type_func(self.value_field.GetValue()))
            )

    def save(self, evt):
        self.save_callback(
            self.name_field.GetValue(),
            self.data_type_func(self.value_field.GetValue()),
            self.tag_type_group.GetString(self.tag_type_group.GetSelection()),
            self.old_name,
        )

        self.Close()


def print_nbt(nbt_data):
    print(nbt_data)


if __name__ == "__main__":
    import wx.lib.inspection

    app = wx.App()
    # wx.lib.inspection.InspectionTool().Show()
    frame = wx.Frame(None)
    NBTEditor(
        frame,
        nbt.TAG_Compound(
            {
                "test1": nbt.TAG_Int(100),
                "test2": nbt.TAG_String("test string"),
                "test3": nbt.TAG_List(
                    [nbt.TAG_Byte(1), nbt.TAG_Byte(2), nbt.TAG_Byte(3), nbt.TAG_Byte(4)]
                ),
                "test4": nbt.TAG_Int_Array(),
            }
        ),
        "tag_compound_test",
        callback=print_nbt,
    )
    frame.Show()
    app.MainLoop()
