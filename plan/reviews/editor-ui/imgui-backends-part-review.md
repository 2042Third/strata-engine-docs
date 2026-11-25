# Part review: `editor-ui/imgui-backends`

- unclear: a callout marked a texture's id as :term[id]{id=id}, the ImGui item ID of `editor-ui/imgui`, a second sense; it and a later "as the id" now say `ImTextureID`.
- gap: "a failed `Init`: the layer then disables ImGui" left out what follows: `ImGuiModule::OnInit` returns false when the layer is not initialized (`ImGuiModule.cpp:45-49`); now "and the program does not run".
